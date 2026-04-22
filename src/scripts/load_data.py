import json
from datetime import datetime, timezone
from typing import List, Dict, Any

from src.config.logger import LoggerConfig
from src.config.manage_db import ManageDB
from src.models.listing import Listing

class LoadData:
    def __init__(self, db: "ManageDB"):
        self.db = db
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    def safe_float(self, value):
        try:
            if value in (None, "", "null"):
                return None
            return float(value)
        except (ValueError, TypeError):
            return None

    def safe_int(self, value):
        try:
            if value in (None, "", "null"):
                return None
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def insert_listings(self, listings_json: List[Dict[str, Any]]) -> None:
        """Insert listings into the database."""
        session = self.db.get_session()
        try:
            if not listings_json:
                self.logger.error("No se recibieron datos para insertar.")
                return
            self.logger.info(f"INSERTANDO {len(listings_json)} REGISTROS EN LA BASE DE DATOS...")
            for item in listings_json:
                self.logger.info({
                    "zpid": item.get("zpid"), ## OK
                    "url": item.get("detailUrl"), ## OK
                    "listing_status": item.get("statusType"),
                    "property_type": item.get("hdpData", {}).get("homeInfo", {}).get("homeType", ""), ## OK
                    "latitude": self.safe_float(item.get("latLong", {}).get("latitude")),
                    "longitude": self.safe_float(item.get("latLong", {}).get("longitude")),
                    "price": self.safe_float(item.get("price").replace("$", "").replace(",", "")) if item.get("price") else None,
                    "bedrooms": self.safe_int(item.get("beds")),
                    "bathrooms": self.safe_int(item.get("baths")),
                    "living_area_sqft": self.safe_float(item.get("area")),
                    "address": item.get("address", ""),
                    "description_length": len(item.get("description", "")) if item.get("description") else 0,
                    "photo_url": item.get("imgSrc", "")
                })
                self.logger.info("")
                self.logger.info("")
                listing = Listing(
                    zpid=item.get("zpid"),
                    url=item.get("detailUrl"),
                    listing_status=item.get("statusType"),
                    property_type=item.get("hdpData", {}).get("homeInfo", {}).get("homeType", ""),
                    latitude=self.safe_float(item.get("latLong", {}).get("latitude")),
                    longitude=self.safe_float(item.get("latLong", {}).get("longitude")),
                    price=self.safe_float(item.get("price").replace("$", "").replace(",", "")) if item.get("price") else None,
                    bedrooms=self.safe_int(item.get("beds")),
                    bathrooms=self.safe_int(item.get("baths")),
                    living_area=self.safe_float(item.get("area")),
                    address=item.get("address", ""),
                    description=item.get("description", "")[:2000] if item.get("description") else None,
                    photo_url=item.get("imgSrc", ""),
                    data=json.dumps(item.get("hdpData", {}).get("homeInfo", {})),
                    scraped_at=datetime.now(timezone.utc).isoformat(),
                    status="done" if item.get("zpid") else "failed"
                )
                session.merge(listing)
            session.commit()
            self.logger.info(f"SE INSERTARON {len(listings_json)} REGISTROS EN LA BASE DE DATOS CON ÉXITO.")
        except Exception as e:
            session.rollback()
            print(f"Error inserting listings: {e}")
            raise
        finally:
            session.close()
