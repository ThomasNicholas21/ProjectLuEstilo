from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, Annotated, List, Union
from datetime import datetime
from pathlib import Path
from src.auth.security.token import get_current_user
from src.common.database import get_db
from src.utils.role_validator import check_admin_permission
from .models import Product
from .schemas import ProductCreate, ProductResponse, ProductUpdate
import uuid
import os
import shutil


product_router = APIRouter(
    prefix="/products",
    tags=["Produtos"],
    responses={
        403: {"description": "Acesso negado"},
        401: {"description": "Credenciais inválidas"}
    }
)



UPLOAD_DIR = Path("media")
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]


@product_router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo produto",
    responses={
        422: {"description": "Dados inválidos"},
        415: {"description": "Formato de imagem não suportado"}
    }
)
async def post_product(
    current_user: dict = Depends(get_current_user),
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
    check_admin_permission(current_user)
    
    try:
        parsed_valid_date = None
        if valid_date:
            try:
                parsed_valid_date = datetime.strptime(valid_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Formato de data inválido. Use YYYY-MM-DD"
                )

        image_path = None
        if image:
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise HTTPException(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    detail="Formatos suportados: JPEG, PNG"
                )
                
            file_ext = image.filename.split('.')[-1]
            filename = f"{uuid.uuid4()}.{file_ext}"
            image_path = str(UPLOAD_DIR / filename)
            
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        product_data = ProductCreate(
            name=name.strip(),
            bar_code=bar_code.strip() if bar_code else None,
            description=description.strip() if description else None,
            price=price,
            stock=stock,
            valid_date=parsed_valid_date,
            category=category.strip() if category else None,
            section=section.strip() if section else None,
            images=image_path
        )

        product = Product(**product_data.model_dump(exclude_none=True))
        
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao salvar produto no banco de dados"
        )
    
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro ao criar cliente: {str(e)}")


@product_router.get(
    "/",
    response_model=List[ProductResponse],
    summary="Listar produtos com filtros",
    responses={
        200: {"description": "Lista de produtos paginada"},
        500: {"description": "Erro interno no servidor"}
    }
)
async def get_products(
    category: Optional[str] = Query(None, example="eletrônicos", description="Filtrar por categoria"),
    price: Optional[float] = Query(None, example=99.90, description="Filtrar por preço exato"),
    available: Optional[bool] = Query(None, example=True, description="Filtrar por disponibilidade em estoque"),
    skip: int = Query(0, ge=0, example=0),
    limit: int = Query(10, ge=1, le=100, example=10),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        query = db.query(Product)

        if category:
            query = query.filter(Product.category.ilike(f"%{category}%"))

        if price is not None:
            query = query.filter(Product.price == price)

        if available is not None:
            query = query.filter(Product.stock > 0 if available else Product.stock == 0)

        return query.offset(skip).limit(limit).all()

    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao consultar produtos"
        )
    
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro insperado: {str(e)}")
    

@product_router.get(
    "/{id_product}",
    response_model=ProductResponse,
    summary="Obter detalhes de um produto",
    responses={
        404: {"description": "Produto não encontrado"},
        500: {"description": "Erro interno no servidor"}
    }
)
async def get_detail_product(
    id_product: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        product = db.query(Product).get(id_product)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto ID {id_product} não encontrado"
            )
        return product
    
    except SQLAlchemyError as e:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar produto"
        )
    
    except Exception as e:
        db.rollback()

        raise HTTPException(status_code=500, detail=f"Erro insperado: {str(e)}")


@product_router.put("/{id_product}", response_model=ProductResponse)
async def put_detail_product(
    id_product: int,
    image: Optional[UploadFile] = File(None),
    data: ProductUpdate = Depends(),
    db: Session = Depends(get_db),
):
    try:
        product = db.query(Product).filter(Product.id_product == id_product).first()
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
