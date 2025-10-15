# 🚖 Taxi Service Backend
Це бекенд служби таксі, створений на FastAPI з підтримкою JWT, Stripe, WebSocket через Redis, Google Maps (опціонально).

## 🚀 Запуск локально
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn taxi_prod:app --reload --host 0.0.0.0 --port 8000
```
Відкрий у браузері: http://127.0.0.1:8000/docs

## ⚙️ Деплой на сервер
Скопіюй проект у /opt/taxi_service, встанови залежності, створи .env, запусти як systemd сервіс.
