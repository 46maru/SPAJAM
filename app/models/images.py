# from database import Base
# from sqlalchemy import Column, Integer, String
# from sqlalchemy.orm import relationship

# from .mixins import TimestampMixin


# class Images(Base, TimestampMixin):
#     __tablename__ = "images"
#     __table_args__ = {"comment": "画像用のテーブル"}
#     id = Column(Integer, autoincrement=True, primary_key=True, comment="画像テーブルのID")
#     image_path = Column("image_path", String(length=512), nullable=False, comment="image_path")
#     tield2 = Column("latitude", nullable=False, comment="tield2")
