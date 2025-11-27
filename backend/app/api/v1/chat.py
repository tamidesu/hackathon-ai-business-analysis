# app/api/v1/chat.py
from typing import Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.dto import RequirementsDocument, RequirementItem
from app.core.logging import logger

router = APIRouter(tags=["chat"])


# какого шага интервью сейчас придерживаемся
CurrentStep = Literal[
    "intro",
    "goal",
    "scope",
    "stakeholders",
    "rules",
    "kpi",
    "flows",
    "constraints",
    "final",
]


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    assistant_message: str
    requirements: Optional[RequirementsDocument] = None
    current_step: CurrentStep
    is_completed: bool = False
    # поле “для будущего мозга”, чтобы AI Architect мог видеть,
    # какие слоты уже заполнены и что спрашивать дальше

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    """
    Временная заглушка, чтобы фронт и команда могли интегрироваться.
    Позже здесь будет вызов реального "мозга" (LangGraph / FSM).
    """
    logger.info("Received chat message: session=%s, text=%s", req.session_id, req.message)

    # Пока: один статический пример документа
    demo_doc = RequirementsDocument(
        project_name="Demo Cashback Project",
        goal="Увеличить удержание клиентов через кешбэк-программу.",
        scope=[
            "Мобильное приложение (iOS/Android)",
            "Интернет-банк (web)",
        ],
        stakeholders=[
            "Директор по розничному бизнесу",
            "Команда цифрового продукта",
            "Отдел рисков",
        ],
        business_rules=[
            "Кешбэк начисляется только верифицированным клиентам.",
            "Максимальный кешбэк в месяц — 50 000 тг.",
        ],
        kpi=[
            "Рост MAU на 15% за 6 месяцев",
            "Увеличение NPS на +10 пунктов",
        ],
        requirements=[
            RequirementItem(
                id="REQ-1",
                title="Отображение кешбэка в профиле",
                description="Клиент должен видеть свой текущий баланс кешбэка в личном кабинете.",
                priority="HIGH",
                status="DRAFT",
            ),
            RequirementItem(
                id="REQ-2",
                title="Уведомление о начислении кешбэка",
                description="После успешной покупки клиент получает пуш / SMS о начислении кешбэка.",
                priority="MED",
                status="DRAFT",
            ),
        ],
        diagram_mermaid=None,
    )

    # В реальности ответ будет зависеть от шага FSM, сообщения пользователя и состояния сессии.
    # Сейчас просто имитируем первый шаг интервью.
    assistant_message = (
        "Привет! Я AI-бизнес-аналитик. Давайте начнём с цели проекта. "
        "Коротко: какую бизнес-задачу вы хотите решить?"
    )

    return ChatResponse(
        assistant_message=assistant_message,
        requirements=demo_doc,
        current_step="goal",
        is_completed=False,
    )