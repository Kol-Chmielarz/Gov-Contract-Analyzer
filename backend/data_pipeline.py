import requests
import pandas as pd
import time
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from database import SessionLocal, Contract

USA_SPENDING_API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

def fetch_contracts(year):
    """Fetch federal contracts from USAspending API by month to ensure 100 unique entries per month."""
    headers = {"Content-Type": "application/json"}
    contracts = []
    max_retries = 5
    initial_delay = 5

    for month in range(1, 13):  # Loop through months
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year}-12-31"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        print(f"📡 Fetching contracts for {year}-{month:02d}...")

        params = {
            "filters": {
                "award_type_codes": ["A", "B", "C", "D"],
                "time_period": [{"start_date": start_date, "end_date": end_date}]
            },
            "fields": [
                "generated_internal_id", "Recipient Name", "Award Amount", "Awarding Agency",
                "Start Date", "End Date", "Funding Agency", "Place of Performance State Code", 
                "Place of Performance Country Code", "Contract Award Type",
                "NAICS Code", "PSC Code", "Total Outlays", "COVID-19 Obligations",
                "Awarding Sub Agency", "Funding Sub Agency"
            ],
            "limit": 100,
            "page": month  # Fetch different pages for different months
        }

        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(USA_SPENDING_API_URL, json=params, headers=headers, timeout=30)

                if response.status_code == 502:
                    wait_time = initial_delay * (2 ** retries)
                    print(f"⚠️ API Error 502. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    retries += 1
                    continue

                if response.status_code != 200:
                    print(f"⚠️ API Error {response.status_code}: {response.text}")
                    return []

                data = response.json()
                monthly_contracts = []

                for award in data.get("results", []):
                    contract = {
                        "contract_id": award.get("generated_internal_id"),
                        "vendor": award.get("Recipient Name", "Unknown"),
                        "award_amount": award.get("Award Amount", 0),
                        "total_outlays": award.get("Total Outlays", 0),
                        "covid_obligations": award.get("COVID-19 Obligations", 0),
                        "agency": award.get("Awarding Agency", "Unknown"),
                        "awarding_sub_agency": award.get("Awarding Sub Agency", "Unknown"),
                        "funding_agency": award.get("Funding Agency", "Unknown"),
                        "funding_sub_agency": award.get("Funding Sub Agency", "Unknown"),
                        "start_date": award.get("Start Date", None),
                        "end_date": award.get("End Date", None),
                        "place_of_performance": f"{award.get('Place of Performance State Code', '')}, {award.get('Place of Performance Country Code', '')}",
                        "contract_category": award.get("Contract Award Type", "Unknown"),
                        "naics_code": award.get("NAICS Code", "Unknown"),
                        "psc_code": award.get("PSC Code", "Unknown")
                    }
                    monthly_contracts.append(contract)

                # Remove duplicates within the same month
                df = pd.DataFrame(monthly_contracts)
                df = df.drop_duplicates(subset=["contract_id"])

                print(f"{len(df)} unique contracts fetched for {year}-{month:02d}")

                contracts.extend(df.to_dict(orient="records"))  # Append filtered contracts
                break  # Exit retry loop if successful

            except requests.exceptions.ReadTimeout:
                wait_time = initial_delay * (2 ** retries)
                print(f"⚠️ Read Timeout: Retrying in {wait_time}s (attempt {retries + 1}/{max_retries})...")
                time.sleep(wait_time)
                retries += 1

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Network error: {e} (attempt {retries + 1}/{max_retries})")
                time.sleep(initial_delay * (2 ** retries))
                retries += 1

        else:
            print(f"Skipping {year}-{month:02d} after multiple failures.")

    print(f"Total {len(contracts)} unique contracts fetched for {year}")
    return contracts

def save_to_db(contracts):
    """Saves contracts to PostgreSQL while skipping duplicates."""
    with SessionLocal() as session:  # Correct session handling
        try:
            inserted_count = 0  # Track inserted records
            duplicate_count = 0  # Track skipped duplicates
            skipped_count = 0  # Track missing data

            if not isinstance(contracts, list):
                print(f"Expected list of contracts but got {type(contracts)}")
                return

            for contract in contracts:
                if not isinstance(contract, dict):
                    print(f"Invalid contract format: {contract}")
                    continue  # Skip invalid contracts

                # Ensure required fields exist
                if not contract.get("contract_id") or contract.get("award_amount") is None:
                    print(f"Skipping contract due to missing ID or amount: {contract}")
                    skipped_count += 1
                    continue

                # Check if contract already exists
                existing_contract = session.query(Contract).filter_by(contract_id=contract["contract_id"]).first()

                if not existing_contract:  # If it's new, insert it
                    new_contract = Contract(**contract)
                    session.add(new_contract)
                    inserted_count += 1
                else:
                    duplicate_count += 1  # Count duplicate contracts

            session.commit()  # Ensure all changes are committed
            print(f"Inserted {inserted_count} new contracts into PostgreSQL.")
            print(f"Skipped {duplicate_count} duplicate contracts.")
            print(f"Skipped {skipped_count} contracts due to missing data.")

            # Check total contracts in DB
            count_query = session.execute(text("SELECT COUNT(*) FROM contracts;"))
            count_result = count_query.fetchone()
            print(f"Total contracts in DB: {count_result[0]}")

        except Exception as e:
            session.rollback()  # Rollback if an error occurs
            print(f"Error saving to DB: {e}")

if __name__ == "__main__":
    years = list(range(2015, 2024))  # Fetch data from 2015-2023
    for year in years:
        print(f"Fetching contracts for {year}...")
        contracts_list = fetch_contracts(year)
        if contracts_list:  # Fix: Check if list is non-empty
            print(f"{len(contracts_list)} contracts ready to be saved for {year}")
            save_to_db(contracts_list)