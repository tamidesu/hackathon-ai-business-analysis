from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import health, publish, chat, preview


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Business Analyst Backend",
        version="1.0.0",
    )

    # CORS для фронта
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(publish.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(preview.router, prefix="/api/v1")

    return app


app = create_app()
