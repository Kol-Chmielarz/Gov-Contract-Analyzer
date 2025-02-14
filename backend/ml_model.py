import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from prophet import Prophet
from sqlalchemy import create_engine, text
from category_encoders import TargetEncoder  
from sklearn.preprocessing import OneHotEncoder

# File Paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

AWARD_MODEL_PATH = os.path.join(MODEL_DIR, "award_prediction.pkl")
FORECAST_MODEL_PATH = os.path.join(MODEL_DIR, "contract_forecast.pkl")
CLUSTER_MODEL_PATH = os.path.join(MODEL_DIR, "agency_clusters.pkl")
ENCODER_PATH = os.path.join(MODEL_DIR, "one_hot_encoder.pkl")
FEATURE_ORDER_PATH = os.path.join(MODEL_DIR, "feature_order.pkl")

# Database Connection
DATABASE_URL = "postgresql://kol:Z0ethed0g!@localhost/gov_contracts"
engine = create_engine(DATABASE_URL)

def train_award_model():
    query = text("""
        SELECT 
            award_amount,
            (end_date - start_date) AS contract_duration,
            agency, funding_agency, place_of_performance, 
            awarding_sub_agency, funding_sub_agency
        FROM contracts
        WHERE award_amount IS NOT NULL
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    print(df.head())
    print(f"Fetched {len(df)} rows from database.")

    if df.empty:
        raise ValueError("No contract data found. Ensure the database is populated.")

    # Drop rows with missing target values
    df.dropna(subset=["award_amount", "contract_duration"], inplace=True)

    categorical_features = ["agency", "funding_agency", "place_of_performance", 
                            "awarding_sub_agency", "funding_sub_agency"]

    df[categorical_features] = df[categorical_features].fillna("UNKNOWN")

    print("Missing values in categorical features:", df[categorical_features].isnull().sum())

    # Fit OneHotEncoder on categorical data
    encoder = OneHotEncoder(handle_unknown="ignore")
    encoded_categorical = encoder.fit_transform(df[categorical_features]).toarray()
    joblib.dump(encoder, ENCODER_PATH)

    # Convert categorical encoding to DataFrame
    encoded_df = pd.DataFrame(encoded_categorical, dtype=float)
    encoded_df.columns = encoded_df.columns.astype(str)  # Ensure all column names are strings

    # Ensure contract duration is included in `X`
    df["contract_duration"] = df["contract_duration"].astype(float)  # Ensure numeric type
    X = pd.concat([encoded_df, df[["contract_duration"]].reset_index(drop=True)], axis=1)
    X.columns = X.columns.astype(str)

    # Ensure `y` is properly aligned and has no missing values
    y = df["award_amount"].reset_index(drop=True)  # Reset index to avoid misalignment

    # Store feature order before training
    feature_order = X.columns.tolist()
    joblib.dump(feature_order, FEATURE_ORDER_PATH)

    # Final consistency check
    if len(X) != len(y):
        print(f"X and y length mismatch: {len(X)} vs {len(y)}")
        min_len = min(len(X), len(y))
        X = X.iloc[:min_len]  # Trim to match
        y = y.iloc[:min_len]  # Trim to match
        print(f"Trimmed to {len(X)} rows")

    # Train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, AWARD_MODEL_PATH)
    print("Award model trained & saved!")

def train_forecast_model():
    query = text("""
        SELECT start_date, COUNT(*) AS contract_count 
        FROM contracts GROUP BY start_date
    """)

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    df.rename(columns={"start_date": "ds", "contract_count": "y"}, inplace=True)

    # Convert to datetime and handle errors
    df["ds"] = pd.to_datetime(df["ds"], errors="coerce")
    df.dropna(subset=["ds"], inplace=True)

    model = Prophet()
    model.fit(df)
    joblib.dump(model, FORECAST_MODEL_PATH)
    print("Forecast model trained & saved!")

def train_agency_clusters():
    query = text("SELECT agency, SUM(award_amount) AS total_award FROM contracts GROUP BY agency")

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    scaler = MinMaxScaler()
    df["scaled_award"] = scaler.fit_transform(df[["total_award"]])

    model = KMeans(n_clusters=3, random_state=42)
    df["cluster"] = model.fit_predict(df[["scaled_award"]])

    joblib.dump(model, CLUSTER_MODEL_PATH)
    print("Agency clustering model trained & saved!")

if __name__ == "__main__":
    train_award_model()
    train_forecast_model()
    train_agency_clusters()
    print("All models trained and saved successfully!")