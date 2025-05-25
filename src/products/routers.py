from fastapi import (
    APIRouter, Depends, HTTPException, 
    UploadFile, File, Form, Query
    )
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.products.models import Product
from src.products.serializer import ProductResponse, ProductBase, ProductUpdate
from src.common.database import get_db
from typing import Optional, Union, List, Annotated
from datetime import datetime
import shutil
import uuid
import os


product_router = APIRouter(prefix="/products", tags=["Products"])
UPLOAD_DIR = "static/images/products"


@product_router.post("/", response_model=ProductResponse)
async def post_product(
    name: str = Form(...),
    bar_code: str = Form(...),
    description: Optional[str] = Form(None),
    price: float = Form(...),
    stock: int = Form(...),
    valid_date: Annotated[
        Optional[datetime],
        Form(
            description="Data de validade no formato YYYY-MM-DD",
            examples=["2025-12-31"]
        )
    ] = None,
    category: Optional[str] = Form(None),
    section: Optional[str] = Form(None),
    image: Optional[Union[UploadFile, str]] = File(None),
    db: Session = Depends(get_db)
):

    try:
        if stock < 0:
            raise HTTPException(
                status_code=422,
                detail="O estoque não pode ser menor que 0"
            )

        description = None if description == "" else description
        category = None if category == "" else category
        section = None if section == "" else section
        
        parsed_valid_date = None
        if valid_date and valid_date != "":
            try:
                parsed_valid_date = datetime.strptime(valid_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=422,
                    detail="Formato de data inválido. Use YYYY-MM-DD"
                )

        image_path = None
        if isinstance(image, str) and image == "":
            image = None
            
        if image and hasattr(image, 'filename') and image.filename:
            ext = image.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            image_path = os.path.join(UPLOAD_DIR, filename)
            
            with open(image_path, 'wb') as buffer:
                shutil.copyfileobj(image.file, buffer)

        product_data = ProductBase(
            name=name,
            bar_code=bar_code,
            description=description,
            price=price,
            stock=stock,
            valid_date=parsed_valid_date,
            category=category,
            section=section
        )

        product = Product(
            **product_data.model_dump(exclude_none=True),
            images=image_path
        )

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=e.errors()
        )
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro ao salvar produto no banco de dados."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado: {str(e)}"
        )
    

@product_router.get("/", response_model=List[ProductResponse])
async def get_products(
    category: Optional[str] = Query(default=None),
    price: Optional[float] = Query(default=None),
    available: Optional[bool] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Product)

        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))

        if price is not None:
            query = query.filter(Product.price == price)

        if available is not None:
            if available:
                query = query.filter(Product.stock > 0)
            else:
                query = query.filter(Product.stock == 0)

        products = query.offset(skip).limit(limit).all()
        return products

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar produtos: {e}")
    

@product_router.get("/{id_product}", response_model=ProductResponse)
async def get_detail_product(id_product: str, db: Session = Depends(get_db)):
    try:
        product = db.query(Product).get(id_product)

        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        
        return product
    
    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {e}")
    
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cliente: {str(e)}")


@product_router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    name: Optional[str] = Form(None),
    bar_code: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[str] = Form(None),
    stock: Optional[str] = Form(None), 
    valid_date: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    section: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    try:
        product = db.query(Product).filter(Product.id_product == product_id).first()

        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        name = None if name == "" else name
        bar_code = None if bar_code == "" else bar_code
        description = None if description == "" else description
        category = None if category == "" else category
        section = None if section == "" else section
        valid_date = None if valid_date == "" else valid_date
        price_value = float(price) if price and price != "" else None
        stock_value = int(stock) if stock and stock != "" else None

        image_path = None
        if isinstance(image, str) and image == "":
            image = None
            
        if image and hasattr(image, 'filename') and image.filename:
            ext = image.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            image_path = os.path.join(UPLOAD_DIR, filename)
            
            with open(image_path, 'wb') as buffer:
                shutil.copyfileobj(image.file, buffer)


        if image.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(status_code=400, detail="Formato de imagem não suportado.")


        if name is not None:
            product.name = name
        if bar_code is not None:
            product.bar_code = bar_code
        if description is not None:
            product.description = description
        if price_value is not None:
            product.price = price_value
        if stock_value is not None:
            product.stock = stock_value
        if valid_date is not None:
            product.valid_date = valid_date
        if category is not None:
            product.category = category
        if section is not None:
            product.section = section
        if image_path is not None:
            product.images = image_path

        db.commit()
        db.refresh(product)
        return product

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Valor inválido: {str(ve)}")
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar produto no banco de dados.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

    
@product_router.delete("/{id_product}")
async def delete_detail_product(id_product: int, db: Session = Depends(get_db)):
    try:
        product = db.query(Product).get(id_product)

        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        db.delete(product)
        db.commit()

        return product

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {e}")
    
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao atualizar cliente: {str(e)}")
