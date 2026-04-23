from datetime import datetime, timezone
import json

from src.models.errors import Errors
from src.config.logger import LoggerConfig
from src.config.manage_db import ManageDB

class LoadErrors:
    def __init__(self, db: ManageDB):
        self.db = db
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    def insert_error(self, error_message):
        """Insert an error message into the database."""
        session = self.db.Session()
        try:
            error = Errors(
                timestamp=datetime.now(timezone.utc).isoformat(),
                error=json.dumps(error_message)
            )
            session.add(error)
            session.commit()
            self.logger.info(f"Error registrado en la base de datos: {error_message}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error inserting error message: {e}")
            raise
        finally:
            session.close()