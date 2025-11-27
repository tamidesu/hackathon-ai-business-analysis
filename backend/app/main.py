from fastapi import FastAPI
from app.api.v1 import health, publish, chat, preview


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Business Analyst Backend",
        version="1.0.0",
    )

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(publish.router, prefix="/api/v1")  # 👈 добавили
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(preview.router, prefix="/api/v1")

    return app

app = create_app()
