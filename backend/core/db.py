from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from models.base import Base
from models.message_model import MessageModel  # Import your models
from core.settings import get_settings
# from settings import settings
settings = get_settings()
engine = create_engine(settings.BASE_DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize the database and create tables if they don't exist."""
    if not database_exists(engine.url):
        create_database(engine.url)
    
    # Create an inspector to check for existing tables
    inspector = inspect(engine)
    
    # Check if messages table exists
    if not inspector.has_table("messages"):
        # Create all tables defined in Base metadata
        Base.metadata.create_all(bind=engine)
        print("Created messages table and related tables")
    else:
        print("Tables already exist")

def get_db():
    """Get a database session."""
    init_db()  # Ensure database and tables exist
    db = SessionLocal()
    try: 
        yield db
    finally: 
        db.close()