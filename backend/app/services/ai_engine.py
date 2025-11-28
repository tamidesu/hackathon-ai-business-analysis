# app/services/ai_engine.py
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from backend_core import app as ai_app  # LangGraph workflow
from app.core.logging import logger


def _history_to_messages(history: List[Dict[str, str]]) -> List[BaseMessage]:
    """
    Конвертируем историю вида:
    [{ "role": "user"|"assistant", "content": "..." }, ...]
    в объекты LangChain (HumanMessage / AIMessage).
    """
    lc_messages: List[BaseMessage] = []

    for m in history:
        role = m.get("role")
        content = m.get("content", "")
        if not content:
            continue

        if role == "assistant":
            lc_messages.append(AIMessage(content=content))
        else:
            # Всё остальное считаем user
            lc_messages.append(HumanMessage(content=content))

    return lc_messages


def run_ai_step(
    history: List[Dict[str, str]],
    user_message: str,
    requirements: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Основной вызов AI-ядра.

    Возвращает финальное состояние TribunalState:
      - messages: список сообщений (Human/AI)
      - requirements: dict с бизнес-требованиями (BusinessRequirements.model_dump())
      - final_report_html: html BRD (если уже сгенерирован)
      - diagram_code: mermaid-диаграмма
      - integration_status: служебный статус
    """
    full_history = history + [{"role": "user", "content": user_message}]
    messages = _history_to_messages(full_history)

    state = {
        "messages": messages,
        "requirements": requirements or {},
        "final_report_html": None,
        "diagram_code": None,
        "integration_status": None,
    }

    logger.info("[AI] Invoke workflow, history_len=%s", len(messages))

    result = ai_app.invoke(state)

    return {
        "messages": result.get("messages", messages),
        "requirements": result.get("requirements", requirements or {}),
        "final_report_html": result.get("final_report_html"),
        "diagram_code": result.get("diagram_code"),
        "integration_status": result.get("integration_status"),
    }
