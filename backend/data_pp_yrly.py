#reruns the year until the target amount is reached in postgres
import requests
import pandas as pd
import time
import random
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from database import SessionLocal, Contract

# 🔽 Change this to fetch contracts for a specific year
YEAR = 2018 
TARGET_CONTRACTS = 1800  # Minimum number of contracts we want per year

USA_SPENDING_API_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"

def get_contract_count(year):
    """Fetches the number of contracts already stored in PostgreSQL for a given year."""
    with SessionLocal() as session:
        count_query = session.execute(text(f"""
            SELECT COUNT(*) FROM contracts WHERE EXTRACT(YEAR FROM start_date) = {year}
        """))
        count_result = count_query.fetchone()
        return count_result[0] if count_result else 0

def fetch_contracts(year, needed_contracts):
    """Fetch additional contracts from the USAspending API using random pages."""
    headers = {"Content-Type": "application/json"}
    contracts = []
    max_retries = 5
    initial_delay = 5

    while needed_contracts > 0:
        month = random.randint(1, 12)  # Pick a random month
        page = random.randint(1, 500)  # Pick a random page for variation

        start_date = f"{year}-{month:02d}-01"
        end_date = f"{year}-{month:02d}-28" if month == 2 else f"{year}-{month:02d}-30"

        print(f"Fetching contracts for {year}-{month:02d}, page {page}...")

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
            "limit": min(needed_contracts, 100),  # Fetch only what's needed up to 100
            "page": page  # Fetch from a random page
        }

        retries = 0
        while retries < max_retries:
            try:
                response = requests.post(USA_SPENDING_API_URL, json=params, headers=headers, timeout=30)

                if response.status_code == 502:
                    wait_time = initial_delay * (2 ** retries)
                    print(f"API Error 502. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    retries += 1
                    continue

                if response.status_code != 200:
                    print(f"API Error {response.status_code}: {response.text}")
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

                df = pd.DataFrame(monthly_contracts)
                df = df.drop_duplicates(subset=["contract_id"])

                print(f"{len(df)} unique contracts fetched for {year}-{month:02d} (page {page})")

                contracts.extend(df.to_dict(orient="records"))  
                needed_contracts -= len(df)  # Reduce the remaining needed count
                break  # Exit retry loop if successful

            except requests.exceptions.ReadTimeout:
                wait_time = initial_delay * (2 ** retries)
                print(f"Read Timeout: Retrying in {wait_time}s (attempt {retries + 1}/{max_retries})...")
                time.sleep(wait_time)
                retries += 1

            except requests.exceptions.RequestException as e:
                print(f"Network error: {e} (attempt {retries + 1}/{max_retries})")
                time.sleep(initial_delay * (2 ** retries))
                retries += 1

        else:
            print(f"Skipping {year}-{month:02d} after multiple failures.")

    return contracts

def save_to_db(contracts):
    """Saves contracts to PostgreSQL while skipping duplicates."""
    with SessionLocal() as session:
        try:
            inserted_count = 0
            duplicate_count = 0
            skipped_count = 0

            if not isinstance(contracts, list):
                print(f"Expected list of contracts but got {type(contracts)}")
                return

            for contract in contracts:
                if not isinstance(contract, dict):
                    print(f"Invalid contract format: {contract}")
                    continue

                if not contract.get("contract_id") or contract.get("award_amount") is None:
                    print(f"Skipping contract due to missing ID or amount: {contract}")
                    skipped_count += 1
                    continue

                existing_contract = session.query(Contract).filter_by(contract_id=contract["contract_id"]).first()

                if not existing_contract:
                    new_contract = Contract(**contract)
                    session.add(new_contract)
                    inserted_count += 1
                else:
                    duplicate_count += 1

            session.commit()
            print(f"Inserted {inserted_count} new contracts into PostgreSQL.")
            print(f"Skipped {duplicate_count} duplicate contracts.")
            print(f"Skipped {skipped_count} contracts due to missing data.")

        except Exception as e:
            session.rollback()
            print(f"Error saving to DB: {e}")

if __name__ == "__main__":
    while True:
        existing_count = get_contract_count(YEAR)
        needed_contracts = TARGET_CONTRACTS - existing_count

        if needed_contracts > 0:
            print(f"Fetching additional contracts for {YEAR}, need {needed_contracts} more...")
            contracts_list = fetch_contracts(YEAR, needed_contracts)

            if contracts_list:
                print(f"{len(contracts_list)} new contracts ready to be saved for {YEAR}")
                save_to_db(contracts_list)
            else:
                print(f"No new contracts found for {YEAR}, retrying...")
            
            time.sleep(10)  # Wait before next attempt to avoid API rate limits

        else:
            print(f"{YEAR} has reached {existing_count} contracts. Fetching complete!")
            break