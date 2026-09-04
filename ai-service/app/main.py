"""SeamlyAI AI-сервис: точка входа FastAPI."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .routes import chat, patterns, providers

STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(
    title="SeamlyAI AI-Service",
    description="AI-микросервис для конструирования одежды: чат (текст/vision) "
    "и генерация лекал по шаблонам VIT.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(patterns.router)
app.include_router(providers.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "seamlyai-ai"}


if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
