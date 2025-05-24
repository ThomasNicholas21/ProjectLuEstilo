from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import ValidationError
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.products.models import Product
from src.products.serializer import ProductResponse, ProductBase
from src.common.database import get_db
from typing import Optional, Union
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
    valid_date: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    section: Optional[str] = Form(None),
    image: Optional[Union[UploadFile, str]] = File(None),
    db: Session = Depends(get_db)
):
    try:
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
    