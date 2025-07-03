import os
import time
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base_class import Base
from app.models import Document, User  


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/mydb")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_connection(max_retries: int = 5, retry_interval: int = 5):
    for attempt in range(max_retries):
        try:
            with engine.connect():
                logger.info(" Successfully connected to PostgreSQL")
                return
        except Exception as e:
            logger.warning(f" DB connection attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                logger.critical(" Could not connect to the database after multiple attempts")
                raise
            time.sleep(retry_interval)


def initialize_models():
   
    from app.models import Document, User 
    Base.metadata.create_all(bind=engine)
    logger.info(" All models initialized (tables created if not exist)")
