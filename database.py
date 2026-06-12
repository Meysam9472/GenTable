from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


load_dotenv()


# Get environment variables
user = os.getenv("POSTGRES_USER")
# Use quote_plus to handle special characters like #, %, $, ^ in password
password = quote_plus(os.getenv("POSTGRES_PASSWORD", ""))
host = os.getenv("POSTGRES_HOST")
port = os.getenv("POSTGRES_PORT")
db_name = os.getenv("POSTGRES_DB")

# Async database setting is for fastapi async apis.
DATABASE_URL = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Base class for models
Base = declarative_base()

# Sync database setting is for celery sync tasks.
SYNC_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

# Create sync engine
sync_engine = create_engine(SYNC_DATABASE_URL)

# Create async session factory
SyncSessionLocal = sessionmaker(bind=sync_engine, autocommit=False, autoflush=False)

