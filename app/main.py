from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.mqtt import mqtt_lifespan
from app.api.routes.command import cmd_router
from app.api.routes.response import response_router
from app.api.routes.export import export_router

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
app.include_router(cmd_router, prefix="/api/v1")
app.include_router(response_router, prefix="/api/v1")
app.include_router(export_router, prefix="/api/v1")
