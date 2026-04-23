from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.config.logger import LoggerConfig
from src.models.base import Base
from src.config.settings import Settings


class ManageDB:
    def __init__(self):
        self.settings = Settings()
        self.db_path = self.settings.DB_PATH
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False, connect_args={"check_same_thread": False})
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.logger = LoggerConfig.get_logger(self.__class__.__name__)

    def get_session(self):
        try:
            return self.Session()
        except Exception as e:
            self.logger.error(f"Error al crear sesión de base de datos: {str(e)}")
            return None

