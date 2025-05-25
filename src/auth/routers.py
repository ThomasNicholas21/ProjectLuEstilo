from fastapi import (
    APIRouter, 
    HTTPException, 
    Depends, 
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
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
    TokenResponse,
    TokenRefreshRequest,
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
    try:
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

    except HTTPException as e:
        raise

    except Exception as e:
        db.rollback()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar usuário."
        )


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    responses={
        200: {"description": "Login bem-sucedido"},
        401: {"description": "Credenciais inválidas"}
    }
)
async def login_user_with_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    try:
        user = db.query(User).filter(User.username == form_data.username).first()

        if not user or not verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas."
            )

        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        refresh_token = create_access_token(
            data={"sub": user.username}, expires_delta=timedelta(days=7)
        )

        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    
    except HTTPException as e:
        raise

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao autenticar usuário."
        )


@auth_router.post(
    "/refresh-token",
    response_model=TokenResponse,
    summary="Refresh de token de acesso",
    responses={
        200: {"description": "Novo token gerado"},
        401: {"description": "Refresh token inválido"}
    }
)
async def refresh_access_token(payload: TokenRefreshRequest):
    try:
        username = decode_refresh_token(payload.refresh_token)
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token inválido ou expirado."
            )
        
        new_access_token = create_access_token(data={"sub": username})
        return TokenResponse(access_token=new_access_token, refresh_token=payload.refresh_token)
    
    except HTTPException as e:
        raise
    
    except Exception as e:
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro inesperado."
        )
