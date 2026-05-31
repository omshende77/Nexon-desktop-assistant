from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Annotated, Optional
from jose import JWTError, jwt

from .database.config import get_db
from .database.models import User
from .database.services.auth_service import (
    verify_password,
    get_password_hash,
    get_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET_KEY,
    ALGORITHM
)
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):

    email = user_data.email.strip() if user_data.email else None

    db_user = get_user(db, username=user_data.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )

    if email:
        email_check = db.query(User).filter(User.email == email).first()
        if email_check:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        username=user_data.username,
        email=email,  # <-- use cleaned email
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    user = get_user(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
