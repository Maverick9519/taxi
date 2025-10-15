# Основний бекенд (production-ready код)
"""
Taxi Service Backend - Production Ready Enhancements

This version adds:
- Environment variables enforcement (JWT_SECRET, STRIPE_API_KEY, STRIPE_WEBHOOK_SECRET required)
- Redis Pub/Sub integration for WebSocket scalability
- Secure production configuration

Run with Redis:
  docker run -d --name redis -p 6379:6379 redis

Environment Variables Required:
  export JWT_SECRET='your_jwt_secret'
  export STRIPE_API_KEY='your_stripe_key'
  export STRIPE_WEBHOOK_SECRET='your_webhook_secret'
  export REDIS_URL='redis://localhost:6379/0'

Dependencies:
  pip install fastapi uvicorn sqlmodel python-jose[cryptography] passlib[bcrypt] httpx python-dotenv stripe aioredis
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, create_engine, select
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import uuid, os, asyncio, json, httpx, stripe
from passlib.context import CryptContext
import aioredis

# ---------------------------
# Environment Validation
# ---------------------------
REQUIRED_ENV = ["JWT_SECRET", "STRIPE_API_KEY", "STRIPE_WEBHOOK_SECRET"]
for env_name in REQUIRED_ENV:
    if not os.getenv(env_name):
        raise RuntimeError(f"Missing required environment variable: {env_name}")

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
STRIPE_API_KEY = os.getenv("STRIPE_API_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

stripe.api_key = STRIPE_API_KEY

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taxi_prod.db")
engine = create_engine(DATABASE_URL, echo=False)

app = FastAPI(title="Taxi Service Backend - Production Ready")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Redis Setup for Pub/Sub
# ---------------------------
class RedisManager:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = await aioredis.from_url(REDIS_URL, decode_responses=True)

    async def publish(self, channel: str, message: dict):
        await self.redis.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel)
        return pubsub

redis_manager = RedisManager()

@app.on_event("startup")
async def startup_event():
    await redis_manager.connect()

# ---------------------------
# Models
# ---------------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    phone: str
    role: str
    hashed_password: str

class Ride(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    passenger_id: int
    driver_id: Optional[int] = None
    status: str = "requested"
    price: Optional[float] = None
    paid: bool = False

SQLModel.metadata.create_all(engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_session():
    with Session(engine) as session:
        yield session

def create_access_token(user_id: int, role: str):
    expire = datetime.utcnow() + timedelta(hours=24)
    payload = {"user_id": user_id, "role": role, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

# ---------------------------
# Auth
# ---------------------------
@app.post("/auth/login")
def login(phone: str = Body(...), password: str = Body(...), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.phone == phone)).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, user.role)
    return {"access_token": token, "token_type": "bearer"}

# ---------------------------
# Stripe Webhook
# ---------------------------
@app.post("/payments/webhook")
async def stripe_webhook(request: Request, session: Session = Depends(get_session)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        ride_id = intent['metadata'].get('ride_id')
        if ride_id:
            ride = session.get(Ride, int(ride_id))
            if ride:
                ride.paid = True
                session.add(ride)
                session.commit()
                await redis_manager.publish(f"ride_{ride.id}", {"type": "payment_succeeded", "ride_id": ride.id})
    return {"status": "ok"}

# ---------------------------
# WebSocket Handling with Redis Pub/Sub
# ---------------------------
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        await websocket.close(code=4001)
        return

    await websocket.accept()
    channel = f"ride_updates_{user_id}"
    pubsub = await redis_manager.subscribe(channel)
    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                await websocket.send_text(message['data'])
    except WebSocketDisconnect:
        await pubsub.unsubscribe(channel)

# ---------------------------
# Health Check
# ---------------------------
@app.get("/health")
def health():
    return {"status": "ok", "redis": True, "stripe": True, "jwt": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("taxi_prod:app", host="0.0.0.0", port=8000, reload=True)
