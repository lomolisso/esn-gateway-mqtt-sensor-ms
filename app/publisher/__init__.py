from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.publisher.api import mqtt_lifespan
from app.publisher.api.routes import api_router

from app.core.config import (
    SECRET_KEY,
    ORIGINS,
)

# --- Init FastAPI ---
app = FastAPI(lifespan=mqtt_lifespan)
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include API Router ---
app.include_router(api_router, prefix="/api/v1")
