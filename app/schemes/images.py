from typing import List
from datetime import datetime
from pydantic import BaseModel

class ImageResponse(BaseModel):
    id: int
    image_path: str | None
    latitude: float | None
    longitude: float | None
    happiness_point: int | None
    happiness_text: str | None
    created_at: datetime | None
    updated_at: datetime

    class Config:
        orm_mode = True

class ImageListResponse(BaseModel):
    results: List[ImageResponse]
    
    class Config:
        orm_mode = True
        
class ImageCreateRequest(BaseModel):
    image_path: str
    latitude: float
    longitude: float
    happiness_point: int
    happiness_text: str
    created_at: datetime

    class Config:
        orm_mode = True