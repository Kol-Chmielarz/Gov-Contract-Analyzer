import requests
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from database import SessionLocal, Contract  # Import DB setup

USA_SPENDING_API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

def fetch_contracts(limit=10):
    """Fetch recent federal contracts from USAspending API."""
    try:
        headers = {"Content-Type": "application/json"}
        params = {
            "filters": {"award_type_codes": ["A", "B", "C", "D"], "agency": "Defense"},
            "fields": ["Award ID", "Recipient Name", "Award Amount", "Awarding Agency"],
            "limit": limit
        }

        response = requests.post(USA_SPENDING_API_URL, json=params, headers=headers)
        response.raise_for_status()
        data = response.json()

        contracts = []
        for award in data.get("results", []):
            contracts.append({
                "contract_id": award.get("Award ID"),
                "vendor": award.get("Recipient Name"),
                "award_amount": award.get("Award Amount"),
                "agency": award.get("Awarding Agency"),
            })

        return pd.DataFrame(contracts)

    except Exception as e:
        print(f"Error fetching USAspending contracts: {e}")
        return pd.DataFrame()

def save_to_db(df):
    """Save contract data to PostgreSQL while avoiding duplicates efficiently."""
    db = SessionLocal()
    try:
        for _, row in df.iterrows():
            stmt = insert(Contract).values(
                contract_id=row["contract_id"],
                vendor=row["vendor"],
                award_amount=row["award_amount"],
                agency=row["agency"]
            ).on_conflict_do_nothing()  # Ignore duplicates

            db.execute(stmt)
        
        db.commit()
        print("✅ Data saved to PostgreSQL!")
    except Exception as e:
        db.rollback()
        print(f"⚠️ Error saving to DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    contracts_df = fetch_contracts(limit=10)
    if not contracts_df.empty:
        save_to_db(contracts_df)