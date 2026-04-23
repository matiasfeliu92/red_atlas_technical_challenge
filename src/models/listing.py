from sqlalchemy import create_engine, Column, String, Integer, Float, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from src.config.settings import Settings

from src.models.base import Base

class Listing(Base):
    __tablename__ = "listings"

    zpid = Column(String, primary_key=True)
    url = Column(String)
    listing_status = Column(String)
    property_type = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    price = Column(Integer)
    bedrooms = Column(Integer)
    bathrooms = Column(Float)
    living_area = Column(Integer)
    address = Column(Text)
    description = Column(Text)
    photo_url = Column(String)
    data = Column(Text)   # JSON completo como string
    scraped_at = Column(String)
    status = Column(String, default="pending")