# app/api/v1/preview.py
from fastapi import APIRouter
from pydantic import BaseModel

from app.models.dto import RequirementsDocument
from app.services.confluence_generator.renderer import render_brd_v2  # имя подправь, если другое
from app.core.logging import logger

router = APIRouter(tags=["preview"])


class PreviewRequest(BaseModel):
    document: RequirementsDocument


class PreviewResponse(BaseModel):
    html: str


@router.post("/preview", response_model=PreviewResponse)
async def preview(req: PreviewRequest) -> PreviewResponse:
    logger.info("[/preview] render preview for project=%s", req.document.project_name)

    html = render_brd_v2(req.document)

    return PreviewResponse(html=html)