import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.dirname(__file__)))  
from fastapi import FastAPI, HTTPException, Query, Depends
from sqlalchemy.orm import Session
import joblib
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.sql import func  
from database import SessionLocal, engine  
from models import Contract  
import numpy as np

# Initialize FastAPI app
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# Database connection
DATABASE_URL = "postgresql://kol:Z0ethed0g!@localhost/gov_contracts"
engine = create_engine(DATABASE_URL)

# Dependency to get database session
def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get backend directory path
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Load Models
award_model = joblib.load(os.path.join(MODEL_DIR, "award_prediction.pkl"))
forecast_model = joblib.load(os.path.join(MODEL_DIR, "contract_forecast.pkl"))
agency_cluster_model = joblib.load(os.path.join(MODEL_DIR, "agency_clusters.pkl"))
ENCODER_PATH = os.path.join(BASE_DIR, "models", "one_hot_encoder.pkl")
FEATURE_ORDER_PATH = os.path.join(MODEL_DIR, "feature_order.pkl")

if not os.path.exists(ENCODER_PATH):
    raise FileNotFoundError(f"Encoder file NOT found at expected path: {ENCODER_PATH}")

print(f"Encoder file found at: {ENCODER_PATH}")  
encoder = joblib.load(ENCODER_PATH)

# ========================== ML ROUTES ========================== #

# Predict Contract Award Amount
@app.get("/api/ml/predict-award")
def predict_award(
    agency: str, 
    place: str, 
    funding_agency: str, 
    awarding_sub_agency: str, 
    funding_sub_agency: str, 
    contract_duration: int
):
    try:
        # Ensure the order matches the training order!
        input_df = pd.DataFrame(
            [[agency, funding_agency, place, awarding_sub_agency, funding_sub_agency]],
            columns=["agency", "funding_agency", "place_of_performance", "awarding_sub_agency", "funding_sub_agency"]
        )

        # Transform the input using the already-fitted encoder
        input_encoded = encoder.transform(input_df).toarray()
        input_encoded_df = pd.DataFrame(input_encoded, dtype=float)
        input_encoded_df.columns = input_encoded_df.columns.astype(str)

        # Add the contract duration
        input_encoded_df["contract_duration"] = float(contract_duration)

        # Reorder the features to match the training order
        feature_order = joblib.load(FEATURE_ORDER_PATH)
        input_encoded_df = input_encoded_df.reindex(columns=feature_order, fill_value=0)

        print(f"Expected features: {award_model.n_features_in_}")  
        print(f"Actual features: {input_encoded_df.shape[1]}")  

        if input_encoded_df.shape[1] != award_model.n_features_in_:
            raise ValueError(
                f"Feature dimension mismatch: Model expects {award_model.n_features_in_}, received {input_encoded_df.shape[1]}"
            )

        prediction = award_model.predict(input_encoded_df)
        return {"predicted_award_amount": round(prediction[0], 2)}
    except Exception as e:
        print(f"Error in predict-award: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# API: Monthly Contract Trends
@app.get("/api/contracts/monthly-trends")
def get_monthly_trends():
    query = text("""
        SELECT 
            EXTRACT(MONTH FROM start_date) AS month,
            COUNT(*) AS contract_count,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY award_amount) AS median_award_amount
        FROM contracts
        WHERE EXTRACT(YEAR FROM start_date) BETWEEN 2015 AND 2024
        GROUP BY month
        ORDER BY month;
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=["month", "contract_count", "median_award_amount"])

    return df.to_dict(orient="records")

# ========================== EXISTING ROUTES ========================== #

# API: Monthly Contract Trends
@app.get("/api/contracts/monthly-trends")
def get_monthly_trends():
    query = text("""
        SELECT 
            EXTRACT(MONTH FROM start_date) AS month,
            COUNT(*) AS contract_count,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY award_amount) AS median_award_amount
        FROM contracts
        WHERE EXTRACT(YEAR FROM start_date) BETWEEN 2015 AND 2024
        GROUP BY month
        ORDER BY month;
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=["month", "contract_count", "median_award_amount"])

    return df.to_dict(orient="records")

# API: Contract Count & Total Award by State (Place of Performance)
@app.get("/api/contracts/place-performance")
def get_place_performance():
    query = text("""
        SELECT place_of_performance, 
               COUNT(*) as contract_count, 
               SUM(award_amount) as total_award
        FROM contracts
        WHERE place_of_performance IS NOT NULL
        GROUP BY place_of_performance
        ORDER BY contract_count DESC
        LIMIT 10;
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=["place_of_performance", "contract_count", "total_award"])

    return df.to_dict(orient="records")

# API: Contract Category Breakdown
@app.get("/api/contracts/category-breakdown")
def get_contract_category_breakdown():
    session = SessionLocal()
    try:
        total_contracts = session.query(func.count(Contract.id)).scalar()

        contract_category_percentages = (
            session.query(
                Contract.contract_category,
                (func.count(Contract.id) / total_contracts) * 100
            )
            .group_by(Contract.contract_category)
            .all()
        )

        results = [{"contract_category": cat, "contract_percentage": perc} for cat, perc in contract_category_percentages]
        return results

    except Exception as e:
        print(f"Error fetching category breakdown: {e}")
        return {"detail": "Error fetching contract category breakdown"}

    finally:
        session.close() 

# API: Top 10 Agencies by Contract Count & Funding
@app.get("/api/contracts/agency-funding")
def get_agency_funding():
    query = text("""
        SELECT agency, 
               COUNT(*) as contract_count, 
               SUM(award_amount) as total_award
        FROM contracts
        GROUP BY agency
        ORDER BY contract_count DESC
        LIMIT 10;
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=["agency", "contract_count", "total_award"])

    return df.to_dict(orient="records")