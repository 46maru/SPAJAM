from database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .mixins import TimestampMixin


class TestItems(Base, TimestampMixin):
    __tablename__ = "test_items"
    __table_args__ = {"comment": "テストアイテム"}
    id = Column(Integer, autoincrement=True, primary_key=True, comment="テストアイテムID")
    field1 = Column("field1", String(length=20), nullable=False, comment="field1")
    tield2 = Column("tield2", String(length=20), nullable=False, comment="tield2")
