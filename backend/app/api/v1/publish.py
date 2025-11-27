# app/api/v1/publish.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

# Импортируем наш DTO
from app.models.dto import RequirementsDocument

# Импортируем клиент (синглтон)
from app.services.confluence import confluence_client

# ! ВАЖНО: Импортируем НОВЫЙ рендерер, который мы написали выше
from app.services.confluence_generator.renderer import render_brd_v2

# Логгер
from app.core.logging import logger

router = APIRouter(tags=["confluence"])


# --- Request / Response Models ---

class PublishRequest(BaseModel):
    session_id: str
    doc: RequirementsDocument
    # Опционально: название родительской страницы (папки проекта)
    parent_title: Optional[str] = None


class PublishResponse(BaseModel):
    confluence_url: str
    page_id: str
    status: str  # 'created' или 'updated'


class ErrorResponse(BaseModel):
    message: str
    error_code: str
    details: Optional[str] = None


# --- API Endpoint ---

@router.post(
    "/publish",
    response_model=PublishResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Server Configuration Error"},
        502: {"model": ErrorResponse, "description": "External Service (Confluence) Error"},
    },
)
async def publish_to_confluence(req: PublishRequest) -> PublishResponse:
    """
    Публикует (или обновляет) BRD страницу в Confluence.

    1. Генерирует HTML (Storage Format) v2.
    2. Проверяет/создает родительскую страницу (если указана).
    3. Ищет существующую страницу по названию.
    4. Создает новую или обновляет существующую (Atomic-like logic).
    """

    # 1. Генерация HTML (Render Step)
    try:
        # Используем наш новый красивый рендерер
        html_body = render_brd_v2(req.doc)
        page_title = f"BRD: {req.doc.project_name}"
    except Exception as e:
        logger.exception("Failed to render BRD HTML document")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Internal error during document generation.",
                "error_code": "RENDER_ERROR",
                "details": str(e)
            }
        )

    # 2. Обработка Parent Page (Опционально)
    parent_id: Optional[str] = None
    if req.parent_title:
        try:
            # Пытаемся найти или создать родителя (папку проекта)
            parent_id = confluence_client.get_or_create_root_page(req.parent_title)
        except Exception as e:
            # ВАЖНО: Если родитель не создался, мы НЕ прерываем публикацию.
            # Мы логируем варнинг и публикуем в корень пространства.
            # Это лучше для UX, чем ошибка.
            logger.warning(f"Could not ensure parent page '{req.parent_title}'. Publishing to root. Error: {e}")
            parent_id = None

    # 3. Взаимодействие с Confluence API
    try:
        # Шаг 3.1: Поиск существующей страницы
        existing_page_id = confluence_client.get_page_id_by_title(page_title)

        diagram_code = """
            flowchart TD
                A[Start] --> B{Goal Defined?}
                B -->|Yes| C[Gather Requirements]
                B -->|No| D[Refine Business Need]
                C --> E[Generate BRD]
                E --> F[Publish to Confluence]
            """

        confluence_client.upload_mermaid_file(existing_page_id, "logic_flow", diagram_code)

        response_data = {}
        operation_status = ""

        if existing_page_id:
            # Шаг 3.2 (А): Обновление
            logger.info(f"Updating existing page ID: {existing_page_id}")
            response_data = confluence_client.update_page(
                page_id=existing_page_id,
                title=page_title,
                html_body=html_body,
                parent_id=parent_id,  # Можно перемещать страницу, если изменился родитель
            )
            operation_status = "updated"
        else:
            # Шаг 3.2 (Б): Создание
            logger.info(f"Creating new page: {page_title}")
            response_data = confluence_client.create_page(
                title=page_title,
                html_body=html_body,
                parent_id=parent_id,
            )
            operation_status = "created"

    except RuntimeError as e:
        # Ошибка конфигурации (нет URL или токена в env)
        logger.error("Confluence configuration missing.")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Server is not configured to talk to Confluence.",
                "error_code": "CONFLUENCE_CONFIG_ERROR"
            }
        ) from e
    except Exception as e:
        # Любая другая ошибка сети или API (401, 403, 503 от Atlassian)
        logger.exception("Confluence API request failed")
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Failed to communicate with Confluence API.",
                "error_code": "CONFLUENCE_API_ERROR",
                "details": str(e)
            }
        ) from e

    # 4. Формирование ответа
    # Извлекаем ссылки из ответа Atlassian API
    links = response_data.get("_links", {})
    base_url = links.get("base", "")
    web_ui = links.get("webui", "")

    # Собираем полный URL (иногда base может отсутствовать в ответе, берем из настроек если надо, 
    # но обычно API возвращает корректные ссылки)
    full_url = base_url + web_ui if base_url and web_ui else ""

    # ID созданной страницы
    final_page_id = response_data.get("id", existing_page_id)

    if not full_url:
        logger.warning("Confluence API did not return a WebUI URL.")
        # Можно попытаться собрать URL вручную из настроек, если критично


    return PublishResponse(
        confluence_url=full_url,
        page_id=str(final_page_id),
        status=operation_status
    )