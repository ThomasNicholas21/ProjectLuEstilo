from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.auth.security.token import get_password_hash
from src.auth.serializer import UserRegister, UserResponse
from src.auth.models import User
from src.common.database import get_db


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
