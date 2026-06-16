import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any

from src.config.settings import Settings
from src.scripts.load_errors import LoadErrors
from src.config.logger import LoggerConfig
from src.config.manage_db import ManageDB

class LoadData:
    def __init__(self, db: ManageDB):
        self.settings = Settings()
        self.db = db
        self.collection = db.db["props"]
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        self.load_errors = LoadErrors(ManageDB())

    def safe_float(self, value):
        try:
            if value in (None, "", "null"):
                return None
            if isinstance(value, str):
                v = value.strip().upper()
                if v.endswith("K"):
                    return float(v[:-1]) * 1000
                if v.endswith("M"):
                    return float(v[:-1]) * 1_000_000
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

    def save_json_file(self, web_path: str, json_data: Any, page_number: int) -> str:
        """Save a JSON file under data/sales or data/rent depending on web_path.

        The filename is <path>_<page_number>_<YYYYMMDD>.json.
        """
        normalized_path = web_path.lower()
        if normalized_path == "sales":
            self.settings.create_dir(self.settings.BASE_DIR, "data", "for_sale")
            output_dir = os.path.join(self.settings.BASE_DIR, "data", "for_sale")
        elif normalized_path == "rentals":
            self.settings.create_dir(self.settings.BASE_DIR, "data", "for_rent")
            output_dir = os.path.join(self.settings.BASE_DIR, "data", "for_rent")
        else:
            self.settings.create_dir(self.settings.BASE_DIR, "data", normalized_path)
            output_dir = os.path.join(self.settings.BASE_DIR, "data", normalized_path)

        os.makedirs(output_dir, exist_ok=True)
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        filename = f"{normalized_path}__{page_number}__{date_str}.json"
        filepath = os.path.join(output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        return filepath

    def insert_listings(self, listings_json: List[Dict[str, Any]]) -> None:
        """Insert listings into the database."""
        try:
            if not listings_json:
                self.load_errors.insert_error({"type": "warning", "message": "No se recibieron datos para insertar."})
                self.logger.warning("No se recibieron datos para insertar.")
                return
            self.logger.info(f"INSERTANDO O ACTUALIZANDO {len(listings_json)} REGISTROS EN LA BASE DE DATOS...")
            for item in listings_json:
                doc = {
                    "zpid": item.get("zpid"),
                    "url": item.get("detailUrl"),
                    "listing_status": item.get("statusType"),
                    "property_type": item.get("hdpData", {}).get("homeInfo", {}).get("homeType", ""),
                    "latitude": self.safe_float(item.get("latLong", {}).get("latitude")),
                    "longitude": self.safe_float(item.get("latLong", {}).get("longitude")),
                    "price": self.safe_float(item.get("price").replace("$", "").replace(",", "")) if item.get("price") else None,
                    "bedrooms": self.safe_int(item.get("beds")),
                    "bathrooms": self.safe_int(item.get("baths")),
                    "living_area": self.safe_float(item.get("area")),
                    "address": item.get("address", ""),
                    "description": item.get("description", "")[:2000] if item.get("description") else None,
                    "photo_url": item.get("imgSrc", ""),
                    "data": item.get("hdpData", {}).get("homeInfo", {}),
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                    "status": "done" if item.get("zpid") else "failed",
                }
                self.logger.info({k: v for k, v in doc.items() if k != "data"})
                self.logger.info("")
                self.collection.update_one(
                    {"zpid": doc["zpid"]},
                    {"$set": doc},
                    upsert=True,
                )
            self.logger.info(f"SE INSERTARON {len(listings_json)} REGISTROS EN LA BASE DE DATOS CON ÉXITO.")
        except Exception as e:
            self.logger.error(f"Error inserting listings: {e}")
            self.load_errors.insert_error({"type": "error", "message": f"Error inserting listings: {str(e)}"})
            raise

