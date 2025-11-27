from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class RequirementItem(BaseModel):
    id: str
    title: str
    description: str
    priority: str  # High, Medium, Low
    status: str  # Draft, Approved, etc.


class RequirementsDocument(BaseModel):
    project_name: str
    goal: str
    scope: List[str] = []

    # Можно оставить List[str], но лучше List[dict], если фронт потянет.
    # Пока оставим List[str] для совместимости, но в рендере будем красиво оформлять.
    stakeholders: List[str] = []

    business_rules: List[str] = []
    kpi: List[str] = []
    requirements: List[RequirementItem] = []
    diagram_mermaid: Optional[str] = None

    # Новые поля для красивой шапки документа
    version: str = Field(default="1.0.0")
    document_status: str = Field(default="DRAFT")  # Draft, Review, Approved
    author: str = Field(default="AI Business Analyst")
    updated_at: datetime = Field(default_factory=datetime.now)