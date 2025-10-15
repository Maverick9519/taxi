# 🚖 Taxi Service Backend

Це бекенд служби таксі, створений на **FastAPI** з підтримкою:
- JWT-аутентифікації
- Stripe платежів
- WebSocket через Redis (для оновлень у реальному часі)
- Google Maps інтеграції (опціонально)

## 🚀 Запуск локально

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn taxi_prod:app --reload --host 0.0.0.0 --port 8000
