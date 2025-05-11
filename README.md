
Visualize Monthly Trends
Dynamic bar and line charts showing monthly contract volume and median award amounts.

Location & Category Insights
Pie and horizontal bar charts breaking down contract percentages by state and contract category.

Machine Learning Predictions
	•	Award Amount Prediction: Estimate contract award values using agency, funding source, location, duration, and sub-agencies.
	•	Forecasting: Project future monthly contract volume using Prophet time series modeling.
	•	Clustering: Discover hidden agency patterns using unsupervised learning (KMeans).

Interactive User Inputs
Select filters for custom ML predictions with dropdown-powered inputs.

frontend
react + Typescript
Tailiwnd CSS
Chart.js
npx create-next-app@latest contract-frontend --ts
cd contract-frontend

npm install axios tailwindcss chart.js react-chartjs-2

npx tailwindcss init -p

Backend
FastAPI
Python
Uvicorn

ML
Scikit-learn, Prophet
Joblib, Pandas
	Award Prediction: RandomForestRegressor trained on:
	•	agency, funding agency, awarding/funding sub-agencies, vendor, location, contract duration
	•	Forecast Model: Prophet-based monthly volume predictor
	•	Clustering: KMeans grouped agency behavior


Data Source
	•	USAspending.gov
	•	Contracts pulled via their free federal API
	•	Stored and queried via PostgreSQL
 
DB
PostgreSQL 

Govitiproj/
├── backend/
│   ├── api.py                  # FastAPI routes & ML endpoints
│   ├── database.py             # SQLAlchemy DB connection
│   ├── ml_model.py             # ML model training logic
│   └── models/                 # Saved ML models (.pkl)
├── frontend/
│   └── src/app/
│       ├── components/         # React components (charts, UI)
│       └── page.tsx           # Main page with routing logic
├── .env                        # PostgreSQL credentials
└── README.md
