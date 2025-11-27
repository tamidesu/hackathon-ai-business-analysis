# app/api/v1/preview.py
from fastapi import APIRouter
from pydantic import BaseModel

from app.models.dto import RequirementsDocument, RequirementItem
from app.services.requirements import render_confluence_storage

router = APIRouter(tags=["preview"])


class PreviewResponse(BaseModel):
    html: str


@router.get("/preview", response_model=PreviewResponse)
async def preview_confluence_document() -> PreviewResponse:
    """
    Отладочный endpoint: генерируем Confluence Storage HTML
    на основе демо-документа (тот же, что в /chat).
    """

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

    html = render_confluence_storage(demo_doc)
    return PreviewResponse(html=html)
