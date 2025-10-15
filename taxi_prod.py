# taxi_prod.py - production-ready backend placeholder
# Если у вас есть полный backend, замените этот файл на ваш.
from fastapi import FastAPI
app = FastAPI()

@app.get('/health')
def health():
    return {'status':'ok'}
