from typing import List
from datetime import datetime
from pydantic import BaseModel

class ImageResponse(BaseModel):
    id: int
    image_path: str
    latitude: float
    longitude: float
    happiness_point: int
    happiness_text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ImageListResponse(BaseModel):
    results: List[ImageResponse]
    
    class Config:
        orm_mode = True