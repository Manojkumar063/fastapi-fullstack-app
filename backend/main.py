from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import ItemCreate, ItemResponse, UserDB, UserCreate, UserResponse, TokenResponse
from auth import get_current_user
from services import auth_service, item_service, chat_service

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Items API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Auth Routes ---

@app.post("/auth/signup", response_model=UserResponse, status_code=201)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.signup_user(user.email, user.password, db)

@app.post("/auth/login", response_model=TokenResponse)
def login(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.login_user(user.email, user.password, db)

@app.get("/auth/me", response_model=UserResponse)
def me(current_user: UserDB = Depends(get_current_user)):
    return current_user

# --- Item Routes ---

@app.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return item_service.create(item.name, item.description, db)

@app.get("/items", response_model=list[ItemResponse])
def list_items(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return item_service.get_all(db)

@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return item_service.get_one(item_id, db)

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db), _=Depends(get_current_user)):
    return item_service.update(item_id, item.name, item.description, db)

@app.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    item_service.delete(item_id, db)

# --- Chat / RAG Routes ---

class ChatRequest(BaseModel):
    question: str

@app.post("/chat/upload")
async def upload_document(file: UploadFile = File(...), current_user: UserDB = Depends(get_current_user)):
    return await chat_service.ingest_document(file, str(current_user.id))

@app.post("/chat/message")
async def chat_message(body: ChatRequest, current_user: UserDB = Depends(get_current_user)):
    return await chat_service.ask_question(body.question, str(current_user.id))

@app.delete("/chat/reset")
def reset_chat(current_user: UserDB = Depends(get_current_user)):
    return chat_service.reset(str(current_user.id))
