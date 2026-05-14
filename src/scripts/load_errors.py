from datetime import datetime, timezone
import json

from src.config.logger import LoggerConfig
from src.config.manage_db import ManageDB

class LoadErrors:
    def __init__(self, db: ManageDB):
        self.db = db
        self.collection = db.db["errors"]
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    def insert_error(self, error_message):
        """Insert an error message into the database."""
        try:
            doc = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": json.dumps(error_message),
            }
            self.collection.insert_one(doc)
            self.logger.info(f"Error registrado en la base de datos: {error_message}")
        except Exception as e:
            self.logger.error(f"Error inserting error message: {e}")
            raise
