from datetime import datetime
from app.models.dto import RequirementsDocument
from .markup import ConfluenceMarkup as CM
from .renderer_brd import render_mermaid_section
from .tables import build_table, TableColumn, render_status_cell, render_priority_with_icon


def render_brd_v2(doc: RequirementsDocument) -> str:
    """
    Главная функция сборки страницы.
    Собирает HTML из "кирпичиков" (макросов).
    """
    parts = []

    # --- 1. Header & Meta Dashboard ---
    parts.append(f"<h1>{CM.escape(doc.project_name)}</h1>")

    # Статус документа (визуальный бейдж)
    doc_status = getattr(doc, "document_status", "DRAFT")
    doc_version = getattr(doc, "version", "1.0.0")

    status_color = "Green" if doc_status.upper() == "APPROVED" else "Yellow"

    # Строка метаданных под заголовком
    meta_line = (
        f"<p>"
        f"<strong>Status:</strong> {CM.status_macro(doc_status, status_color)} &nbsp; "
        f"<strong>Version:</strong> <tt>{CM.escape(doc_version)}</tt>"
        f"</p>"
    )
    parts.append(meta_line)

    # --- 2. Executive Summary (Layout: 2 Columns) ---
    updated_at = getattr(doc, "updated_at", datetime.now())
    time_macro = CM.time_macro(updated_at)
    author = getattr(doc, "author", "AI Analyst")

    left_content = (
        f"<h3>🎯 Project Goal</h3>"
        f"<p style='font-size: 1.1em;'>{CM.escape(doc.goal)}</p>"
    )

    right_content = (
        f"<h3>ℹ️ Document Info</h3>"
        f"<table style='width: 100%; border: none;'>"
        f"<tr><td style='border: none; color: #5e6c84;'>Author:</td><td style='border: none;'>{CM.escape(author)}</td></tr>"
        f"<tr><td style='border: none; color: #5e6c84;'>Updated:</td><td style='border: none;'>{time_macro}</td></tr>"
        f"</table>"
    )

    parts.append(CM.layout_section([left_content, right_content], type="two_equal"))
    parts.append("<hr/>")

    # --- 3. Scope & Business Rules ---
    parts.append("<h2>🔭 Scope & Business Rules</h2>")

    # Scope (Left)
    if doc.scope:
        scope_items = "".join([f"<li>{s}</li>" for s in doc.scope])
        scope_html = f"<ul>{scope_items}</ul>"
        scope_panel = CM.success_panel(scope_html, title="In Scope")
    else:
        scope_panel = CM.info_panel("Scope items not defined yet.", title="Scope Empty")

    # Business Rules (Right)
    if doc.business_rules:
        rules_items = "".join([f"<li>{r}</li>" for r in doc.business_rules])
        rules_html = f"<ul>{rules_items}</ul>"
        rules_panel = CM.warning_panel(rules_html, title="Constraints")
    else:
        rules_panel = CM.info_panel("No specific business rules defined.", title="Rules")

    parts.append(CM.layout_section([scope_panel, rules_panel], type="two_equal"))

    # --- 4. Stakeholders & KPI ---
    parts.append("<h2>👥 Stakeholders & KPI</h2>")

    sh_content = ""
    if doc.stakeholders:
        sh_items = "".join([f"<li>{s}</li>" for s in doc.stakeholders])
        sh_content = f"<ul>{sh_items}</ul>"
    else:
        sh_content = "<p><em>No stakeholders listed.</em></p>"

    kpi_content = ""
    if doc.kpi:
        kpi_items = "".join([f"<li>{k}</li>" for k in doc.kpi])
        kpi_content = f"<ul>{kpi_items}</ul>"
    else:
        kpi_content = "<p><em>No KPIs defined.</em></p>"

    parts.append(CM.layout_section([sh_content, kpi_content], type="two_equal"))

    # --- 5. Functional Requirements (THE CORE) ---
    parts.append("<h2>📝 Functional Requirements</h2>")

    if doc.requirements:
        # Используем ПРОЦЕНТЫ для ширины, чтобы таблица была на весь экран
        columns = [
            TableColumn(key="id", header="ID", width="10%", align="center"),
            TableColumn(key="title", header="Requirement Title", width="25%"),
            # Description получает 45%, чтобы занимать максимум места
            TableColumn(key="description", header="Description / User Story", width="45%"),
            TableColumn(key="priority", header="Priority", width="10%", align="center",
                        renderer=render_priority_with_icon),
            TableColumn(key="status", header="Status", width="10%", align="center", renderer=render_status_cell),
        ]

        rows = [req.dict() for req in doc.requirements]
        parts.append(build_table(columns, rows))
    else:
        parts.append(CM.info_panel("No requirements added yet.", title="Requirements Draft"))

    # --- 6. Diagrams (Mermaid) ---
    if doc.diagram_mermaid:
        parts.append("<h2>📊 Logic Flow (Diagram)</h2>")

        # 1. Генерируем макрос для плагина Stratus Add-ons
        mermaid_macro_html = CM.mermaid_macro(doc.diagram_mermaid)
        parts.append(mermaid_macro_html)

        # 2. Исходный код под спойлером (для удобства копирования)
        mermaid_code_block = CM.code_block(doc.diagram_mermaid, language="mermaid")
        parts.append(CM.expand_block("Show Mermaid Source Code", mermaid_code_block))

    # --- 7. Footer ---
    footer = (
        "<p style='text-align: center; color: #97a0af; font-size: 0.85em; margin-top: 30px;'>"
        "Generated by <strong>AI Business Analyst</strong>. "
        "Content is based on the latest interview session."
        "</p>"
    )
    parts.append(footer)

    return "\n".join(parts)
