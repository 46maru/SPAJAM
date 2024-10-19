from database import Base
from sqlalchemy import Column, Integer, String, Double, DateTime
from sqlalchemy.orm import relationship

from .mixins import TimestampMixin


class Images(Base, TimestampMixin):
    __tablename__ = "images"
    __table_args__ = {"comment": "画像用のテーブル"}
    id = Column(Integer, autoincrement=True, primary_key=True, comment="画像テーブルのID")
    image_path = Column("image_path", String(length=256), nullable=False, comment="画像のパス")
    latitude = Column("latitude", Double, comment="緯度")
    longitude = Column("longitude", Double, comment="経度")
    happiness_point = Column("happiness_point", Integer, comment="幸福度ポイント")
    happiness_text = Column("happiness_text", String(length=1024), comment="幸福度テキスト")
    created_at = Column("created_at", DateTime(timezone=True), comment="作成日時")