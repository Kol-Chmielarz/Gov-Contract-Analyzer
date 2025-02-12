from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import psycopg2

# PostgreSQL Connection String
DATABASE_URL = "postgresql://kol:Z0ethed0g!@localhost/gov_contracts"

# Create the database if it doesn't exist
def create_database():
    conn = psycopg2.connect("dbname=postgres user=kol password=yZ0ethed0g! host=localhost")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname='gov_contracts'")
    exists = cur.fetchone()
    if not exists:
        cur.execute("CREATE DATABASE gov_contracts")
        print("✅ Database 'gov_contracts' created!")
    cur.close()
    conn.close()

create_database()

# Set up DB engine & session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Define Contracts Table
class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    contract_id = Column(String, unique=True)
    vendor = Column(String)
    award_amount = Column(Float)
    agency = Column(String)

# Create Table
Base.metadata.create_all(engine)