from fastapi import APIRouter, FastAPI, Depends,File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.images import Images
from schemes.images import ImageListResponse
from database import get_db
from typing import List
from datetime import datetime
from fastapi.responses import JSONResponse
import base64

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

@router.post('/api/image')
async def create_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    encoded_image = base64.b64encode(contents).decode('utf-8')
    image = Images(image_path=encoded_image, created_at=datetime.now(), updated_at=datetime.now())
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


app.include_router(router)


