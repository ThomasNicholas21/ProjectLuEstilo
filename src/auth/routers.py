from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.auth.security.token import get_password_hash
from src.auth.serializer import UserRegister, UserResponse, UserLogin
from src.auth.serializer import TokenResponse, TokenRefreshRequest
from src.auth.models import User
from datetime import timedelta
from src.common.database import get_db
from src.auth.security.token import verify_password, create_access_token
from src.auth.security.token import decode_refresh_token


auth_router = APIRouter(prefix="/auth", tags=["User"])


@auth_router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username já está em uso.")

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


@auth_router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()

    if not existing_user:
        raise HTTPException(
            status_code=401,
            detail="Usuário não encontrado."
        )

    if not verify_password(user_data.password, existing_user.password):
        raise HTTPException(
            status_code=401,
            detail="Senha incorreta."
        )

    access_token = create_access_token(data={"sub": existing_user.username})
    refresh_token = create_access_token(data={"sub": existing_user.username}, expires_delta=timedelta(days=7))

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
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
