from fastapi import APIRouter, FastAPI, Depends, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models.images import Images
from schemes.images import ImageListResponse
from database import get_db
from typing import List
from datetime import datetime, time
from fastapi.responses import JSONResponse
import base64
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import exif
from function.akinori import get_image_metadata, convert_to_image_data, analyze_multiple_images
from openai import AzureOpenAI
import json


app = FastAPI(debug=True)
router = APIRouter()

origins = ["*"]
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
    try:
        contents = await file.read()
        
        # 一時的にファイルを保存
        with open("temp_image.jpg", "wb") as temp_file:
            temp_file.write(contents)
        
        # メタデータを取得
        metadata = get_image_metadata("temp_image.jpg")
        
        # 画像データを変換
        image_data = convert_to_image_data("temp_image.jpg", metadata)
        
        # 緯度と経度を取得
        latitude = image_data['metadata']['緯度']
        longitude = image_data['metadata']['経度']
        
        # Base64エンコード
        encoded_image = base64.b64encode(contents).decode('utf-8')
        
        # データベースに保存
        image = Images(
            image_path=encoded_image,
            latitude=str(latitude) if latitude else None,
            longitude=str(longitude) if longitude else None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        
        return image
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 一時ファイルを削除
        import os
        if os.path.exists("temp_image.jpg"):
            os.remove("temp_image.jpg")

@router.delete('/api/image/{image_id}')
def delete_image(image_id: int, db: Session = Depends(get_db)):
    # データベースから指定されたIDの画像を取得
    image = db.query(Images).filter(Images.id == image_id).first()
    
    # 画像をデータベースから削除
    db.delete(image)
    db.commit()
    return {"message": f"Image with id {image_id} has been successfully deleted"}
    
@router.get('/api/happiness')
async def get_happiness(db: Session = Depends(get_db)):
    # 今日の日付を取得
    today = datetime.now().date()
    
    # 今日の開始時刻と終了時刻を設定
    today_start = datetime.combine(today, time.min)
    today_end = datetime.combine(today, time.max)
    
    # 本日作成された画像を取得
    today_images = db.query(Images).filter(
        Images.created_at.between(today_start, today_end)
    ).all()
    
    # Base64エンコードされた画像のリストを作成
    base64_images = []
    for image in today_images:
        base64_images.append(image.image_path)
        
    #画像分析を実行
    if base64_images:
        analysis_result = analyze_multiple_images(base64_images)
    else:
        analysis_result = "本日の画像がありません。"
    
    data = json.loads(analysis_result)
    # 新しい形式に変換
    output_data = {
        'score': data['score'],
        'comment': data['comments']
    }
    
    return output_data

app.include_router(router)


