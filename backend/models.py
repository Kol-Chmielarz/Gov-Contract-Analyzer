from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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