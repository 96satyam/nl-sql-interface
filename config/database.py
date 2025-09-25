from sqlalchemy import create_engine
from config import settings

def get_db_engine():
    """
    Creates and returns a SQLAlchemy engine for the PostgreSQL database.
    """
    # Create the database connection URL
    db_url = (
        f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    
    # Create the SQLAlchemy engine
    engine = create_engine(db_url)
    return engine