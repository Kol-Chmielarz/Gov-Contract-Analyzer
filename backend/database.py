from sqlalchemy import create_engine, Column, Integer, String, Float, Date
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
        print("Database 'gov_contracts' created!")
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

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(String(50), unique=True, index=True, nullable=False)
    vendor = Column(String(255), nullable=True)
    award_amount = Column(Float, nullable=False)
    total_outlays = Column(Float, nullable=True)  
    covid_obligations = Column(Float, nullable=True)  
    agency = Column(String(255), nullable=False)
    awarding_sub_agency = Column(String(255), nullable=True)  
    funding_agency = Column(String(255), nullable=True)
    funding_sub_agency = Column(String(255), nullable=True)  
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    place_of_performance = Column(String(100), nullable=True)
    contract_category = Column(String(50), nullable=True)
    naics_code = Column(String(50), nullable=True)  
    psc_code = Column(String(50), nullable=True)

# Create Table
Base.metadata.create_all(engine)