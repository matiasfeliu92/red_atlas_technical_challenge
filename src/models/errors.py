from sqlalchemy import create_engine, Column, String, Integer, Float, Text
from src.models.base import Base


class Errors(Base):
    __tablename__ = "errors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String)
    error = Column(Text)