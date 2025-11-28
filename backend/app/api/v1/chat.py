# app/api/v1/chat.py
from typing import Literal, Optional, List, Dict, Any

from fastapi import APIRouter
from pydantic import BaseModel

from langchain_core.messages import AIMessage, BaseMessage

from app.models.dto import RequirementsDocument
from app.core.logging import logger
from app.services.ai_engine import run_ai_step

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

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    # фронт может слать историю, чтобы бэк был stateless
    history: List[ChatMessage] = []
    # на будущее: если хочешь хранить requirements на фронте и слать обратно
    requirements: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    assistant_message: str
    requirements: Optional[RequirementsDocument] = None
    current_step: CurrentStep
    is_completed: bool = False
    diagram_mermaid: Optional[str] = None
    final_report_html: Optional[str] = None


def _extract_last_ai_message(messages: List[BaseMessage]) -> str:
    for m in reversed(messages):
        if isinstance(m, AIMessage):
            return m.content
    # fallback
    return "Извините, не удалось получить ответ от модели."


def _detect_step(reqs: Dict[str, Any], final_html: Optional[str]) -> CurrentStep:
    """
    Очень простая эвристика, чтобы фронт понимал, на каком шаге мы сейчас.
    Можно потом улучшить под реальную структуру BusinessRequirements.
    """
    if final_html:
        return "final"

    # дальше смотрим по заполненности полей требований
    if not reqs.get("goal"):
        return "intro"  # или "goal", если хочешь сразу на цель
    if not reqs.get("scope"):
        return "scope"
    if not reqs.get("stakeholders"):
        return "stakeholders"
    if not reqs.get("business_rules"):
        return "rules"
    if not reqs.get("kpi"):
        return "kpi"
    if not reqs.get("flows"):
        return "flows"
    if not reqs.get("constraints"):
        return "constraints"

    # если всё есть, но финального HTML ещё нет — считаем, что на constraints
    return "constraints"

def _to_requirements_document(reqs: Dict[str, Any]) -> RequirementsDocument:
    """
    Маппинг из BusinessRequirements (dict) в наш RequirementsDocument.
    Пока делаем простой вариант. Позже можно обогатить (user stories → requirements и т.д.).
    """
    return RequirementsDocument(
        project_name=reqs.get("project_name", "Новый проект"),
        goal=reqs.get("goal", ""),
        scope=reqs.get("scope", []),
        stakeholders=reqs.get("stakeholders", []),
        # BusinessRequirements.recommendations → business_rules (как советы/ограничения)
        business_rules=reqs.get("recommendations", []),
        kpi=[],
        requirements=[],
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    logger.info(
        "[/chat] session=%s message=%s",
        request.session_id,
        request.message,
    )

    history_dicts = [m.model_dump() for m in request.history]

    ai_state = run_ai_step(
        history=history_dicts,
        user_message=request.message,
        requirements=request.requirements or {},
    )

    messages: List[BaseMessage] = ai_state["messages"]
    reqs_raw: Dict[str, Any] = ai_state["requirements"] or {}

    assistant_message = _extract_last_ai_message(messages)
    current_step = _detect_step(reqs_raw, ai_state["final_report_html"])
    is_completed = ai_state["final_report_html"] is not None

    # Если требований ещё нет — можно вернуть None
    requirements_doc: Optional[RequirementsDocument] = None
    if reqs_raw:
        requirements_doc = _to_requirements_document(reqs_raw)

    return ChatResponse(
        assistant_message=assistant_message,
        requirements=requirements_doc,
        current_step=current_step,
        is_completed=is_completed,
        diagram_mermaid=ai_state["diagram_code"],
        final_report_html=ai_state["final_report_html"],
    )