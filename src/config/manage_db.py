from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.models.listing import Base
from src.config.settings import Settings


class ManageDB:
    def __init__(self):
        self.settings = Settings()
        self.db_path = self.settings.DB_PATH
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
