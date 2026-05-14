from pymongo import MongoClient

from src.config.logger import LoggerConfig
from src.config.settings import Settings


class ManageDB:
    def __init__(self):
        self.settings = Settings()
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)
        try:
            self.client = MongoClient(self.settings.MONGO_URI)
            self.db = self.client[self.settings.MONGO_DB_NAME]
            self.logger.info(f"Conectado a MongoDB: {self.settings.MONGO_DB_NAME}")
        except Exception as e:
            self.logger.error(f"Error al conectar a MongoDB: {str(e)}")
            raise

