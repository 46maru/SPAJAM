from fastapi import APIRouter, FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.images import Images
from schemes.images import ImageListResponse
from database import get_db
from typing import List
from datetime import datetime

app = FastAPI(debug=True)
router = APIRouter()

origins = ["localhost"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@router.get('/check')
def check():
    return {"message": "Hello, FastAPI!"}

@router.get('/api/image', response_model=ImageListResponse)
def get_image(db: Session = Depends(get_db)):
    images = db.query(Images).all()
    return ImageListResponse(results=images)



app.include_router(router)


