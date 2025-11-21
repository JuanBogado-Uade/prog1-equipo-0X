# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import router

app = FastAPI(title="Torneo Fútbol API - MVP 0.1")

# TODO: Restringir la configuración de CORS para permitir únicamente
#       solicitudes HTTPS específicas desde el frontend autorizado,
#       en lugar de habilitar todos los orígenes y métodos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")