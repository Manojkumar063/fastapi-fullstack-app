from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import UserDB
from auth import hash_password, verify_password, create_access_token


def signup_user(email: str, password: str, db: Session):
    if db.query(UserDB).filter(UserDB.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = UserDB(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(email: str, password: str, db: Session):
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_access_token({"sub": user.email})}
