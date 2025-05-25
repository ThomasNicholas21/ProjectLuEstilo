from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import timedelta
from .security.token import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_refresh_token
)
from .schemas import (
    UserRegister,
    UserResponse,
    UserLogin,
    TokenResponse,
    TokenRefreshRequest
)
from .models import User
from src.common.database import get_db


auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"description": "Credenciais inválidas"},
        400: {"description": "Requisição mal formatada"}
    }
)


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    responses={
        201: {"description": "Usuário criado com sucesso"},
        400: {"description": "Nome de usuário já existe"}
    }
)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome de usuário já está em uso."
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        password=hashed_password,
        role=user_data.role.value  
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    responses={
        200: {"description": "Login bem-sucedido"},
        401: {"description": "Credenciais inválidas"}
    }
)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas."
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@auth_router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(payload: TokenRefreshRequest):
    username = decode_refresh_token(payload.refresh_token)

    if not username:
        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido ou expirado."
        )

    new_access_token = create_access_token(data={"sub": username})
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=payload.refresh_token, 
        token_type="bearer"
    )
