from fastapi import (
    APIRouter, Depends, HTTPException, 
    UploadFile, File, Form, Query
    )
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.products.models import Product
from src.products.serializer import ProductResponse, ProductBase, ProductUpdate, ProductCreate
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
    name: Union[str, None] = Form(...),
    bar_code: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Union[float, None] = Form(...),
    stock: Union[int, None] = Form(...),
    valid_date: Annotated[
        Optional[str],
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
        if not name or name.strip() == "":
            raise HTTPException(status_code=422, detail="O nome do produto é obrigatório.")
        
        if price is None:
            raise HTTPException(status_code=422, detail="O preço é obrigatório.")
        
        if stock is None:
            raise HTTPException(status_code=422, detail="O estoque é obrigatório.")

        name = name.strip()
        bar_code = None if bar_code == "" else bar_code
        description = None if description == "" else description
        category = None if category == "" else category
        section = None if section == "" else section
        valid_date = None if valid_date == "" else valid_date

        try:
            price_value = float(price)

        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="Preço inválido. Use um número.")

        try:
            stock_value = int(stock)

        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="Estoque inválido. Use um número inteiro.")
        
        if stock_value < 0:
            raise HTTPException(status_code=422, detail="O estoque não pode ser menor que 0.")

        parsed_valid_date = None
        if valid_date:
            try:
                parsed_valid_date = datetime.strptime(valid_date, "%Y-%m-%d")

            except ValueError:
                raise HTTPException(status_code=422, detail="Formato de data inválido. Use YYYY-MM-DD")

        image_path = None
        if isinstance(image, str) and image == "":
            image = None

        if image and hasattr(image, "filename") and image.filename:
            if image.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="Formato de imagem não suportado.")

            ext = image.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            image_path = os.path.join(UPLOAD_DIR, filename)

            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        product_data = ProductCreate(
            name=name,
            bar_code=bar_code,
            description=description,
            price=price_value,
            stock=stock_value,
            valid_date=parsed_valid_date,
            category=category,
            section=section,
            images=image_path
        )

        product = Product(**product_data.model_dump(exclude_none=True))

        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao salvar produto no banco de dados.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")


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
async def put_detail_product(
    product_id: int,
    image: Optional[UploadFile] = File(None),
    data: ProductUpdate = Depends(),
    db: Session = Depends(get_db),
):
    try:
        product = db.query(Product).filter(Product.id_product == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        parsed_valid_date = None
        if data.valid_date:
            try:
                parsed_valid_date = datetime.strptime(data.valid_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=422, detail="Formato de data inválido. Use YYYY-MM-DD")

        image_path = None
        if image and hasattr(image, 'filename') and image.filename:
            if image.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(status_code=400, detail="Formato de imagem não suportado.")
            ext = image.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            image_path = os.path.join(UPLOAD_DIR, filename)
            with open(image_path, 'wb') as buffer:
                shutil.copyfileobj(image.file, buffer)

        update_fields = {
            "name": data.name,
            "bar_code": data.bar_code,
            "description": data.description,
            "price": data.price,
            "stock": data.stock,
            "valid_date": parsed_valid_date,
            "category": data.category,
            "section": data.section,
            "images": image_path if image_path else None
        }

        for field, value in update_fields.items():
            if value is not None:
                setattr(product, field, value)

        db.commit()
        db.refresh(product)
        return product

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar produto no banco de dados.")
    except Exception as e:
        db.rollback()
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
