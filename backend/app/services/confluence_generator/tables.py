from typing import List, Dict, Any, Callable, Optional
from pydantic import BaseModel
from .markup import ConfluenceMarkup as CM


class TableColumn(BaseModel):
    key: str
    header: str
    renderer: Optional[Callable[[Any], str]] = None
    width: Optional[str] = None  # Example: "100px", "10%", "40"
    align: str = "left"  # left, center, right


def build_table(columns: List[TableColumn], rows: List[Dict[str, Any]]) -> str:
    """
    Генерирует HTML таблицу с поддержкой ширины колонок и выравнивания.
    """

    # 1. Colgroup (Фиксируем ширину колонок)
    cols_def = ""
    for col in columns:
        width_attr = f'style="width: {col.width};"' if col.width else ""
        cols_def += f'<col {width_attr}/>'

    colgroup = f"<colgroup>{cols_def}</colgroup>"

    # 2. Header
    header_cells = ""
    for col in columns:
        header_cells += f'<th style="text-align: {col.align};">{CM.escape(col.header)}</th>'
    header_row = f"<tr>{header_cells}</tr>"

    # 3. Body
    body_rows = ""
    for row_data in rows:
        cells = ""
        for col in columns:
            val = row_data.get(col.key)

            # Custom Renderer
            if col.renderer:
                content = col.renderer(val)
            else:
                # Default text renderer with Empty State handling
                if val is None or str(val).strip() == "":
                    content = '<span style="color: #97a0af;">-</span>'
                else:
                    content = CM.escape(str(val))

            cells += f'<td style="text-align: {col.align};">{content}</td>'
        body_rows += f"<tr>{cells}</tr>"

    # ВАЖНО: width: 100% растягивает таблицу на весь экран
    return f"""
    <table style="width: 100%;">
        {colgroup}
        <tbody>
            {header_row}
            {body_rows}
        </tbody>
    </table>
    """


# --- RENDERERS ---

def render_status_cell(status: str) -> str:
    if not status:
        return CM.status_macro("Draft", "Grey", subtle=True)

    s = status.upper()

    mapping = {
        "DRAFT": ("Draft", "Grey"),
        "TO DO": ("To Do", "Blue"),
        "IN PROGRESS": ("In Progress", "Blue"),
        "REVIEW": ("In Review", "Yellow"),
        "DONE": ("Done", "Green"),
        "APPROVED": ("Approved", "Green"),
        "REJECTED": ("Rejected", "Red"),
        "BLOCKED": ("Blocked", "Red"),
        "HIGH": ("High", "Red"),
        "MEDIUM": ("Medium", "Yellow"),
        "LOW": ("Low", "Green"),
    }

    title, color = mapping.get(s, (status.capitalize(), "Grey"))
    return CM.status_macro(title, color)


def render_priority_with_icon(priority: str) -> str:
    """Приоритет с иконкой (стрелочкой)"""
    if not priority:
        return ""
    p = priority.upper()
    if "HIGH" in p:
        return f'<span style="color: #de350b;"><strong>↑ {CM.escape(priority)}</strong></span>'
    if "LOW" in p:
        return f'<span style="color: #00875a;">↓ {CM.escape(priority)}</span>'
    return CM.escape(priority)


def render_list_as_tags(items: List[str]) -> str:
    """Рендерит список строк как красивые теги внутри ячейки"""
    if not items:
        return ""
    tags_html = " ".join([
        f'<span style="background-color: #ebecf0; color: #172b4d; padding: 2px 6px; border-radius: 3px; font-size: 12px; margin-right: 4px; display: inline-block;">{CM.escape(i)}</span>'
        for i in items
    ])
    return tags_html