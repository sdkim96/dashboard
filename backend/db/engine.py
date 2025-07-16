from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import CONFIG

engine = create_engine(
    url=CONFIG.database_url,
)
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    
)