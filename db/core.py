import databases
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "sqlite:///./test.db"
# DATABASE_URL = "postgresql://user:password@postgresserver/db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)
Base = declarative_base()
