# 🚖 Taxi Service Backend (Demo)
This archive contains a demo backend (FastAPI) and a minimal React frontend for testing.

## Run backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn taxi_prod:app --reload --host 0.0.0.0 --port 8000

## Run frontend
cd frontend
npm install
npm start
