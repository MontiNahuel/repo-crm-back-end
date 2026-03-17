import socketio
from fastapi import FastAPI

# 1. Tu app de FastAPI normal (asumo que ya la tenés instanciada)
app = FastAPI()

# 2. El servidor de Socket.IO (Fijate que dice AsyncServer y async_mode='asgi')
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

@sio.event
async def connect(sid, environ):
    print('🟢 Cliente conectado:', sid)

@sio.event
async def disconnect(sid):
    print('🔴 Cliente desconectado:', sid)