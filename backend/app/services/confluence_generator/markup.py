import base64
import html
import json
from typing import List, Literal


class ConfluenceMarkup:
    """
    Генератор Storage Format (XHTML) для Confluence.
    Версия: Production (Full)
    Включает: Layouts, Code Blocks, Dates, Icons, Mermaid.
    """

    @staticmethod
    def escape(text: str) -> str:
        return html.escape(str(text)) if text else ""

    # --- ПАНЕЛИ (С иконками и без) ---
    @staticmethod
    def _panel(macro_name: str, content: str, title: str = None) -> str:
        title_block = f'<ac:parameter ac:name="title">{ConfluenceMarkup.escape(title)}</ac:parameter>' if title else ""
        return f"""
        <ac:structured-macro ac:name="{macro_name}">
            {title_block}
            <ac:rich-text-body>{content}</ac:rich-text-body>
        </ac:structured-macro>
        """

    @staticmethod
    def info_panel(content: str, title: str = None) -> str:
        return ConfluenceMarkup._panel("info", content, title)

    @staticmethod
    def success_panel(content: str, title: str = None) -> str:
        return ConfluenceMarkup._panel("tip", content, title)

    @staticmethod
    def warning_panel(content: str, title: str = None) -> str:
        return ConfluenceMarkup._panel("note", content, title)

    @staticmethod
    def error_panel(content: str, title: str = None) -> str:
        return ConfluenceMarkup._panel("warning", content, title)

    # --- СТАТУСЫ И БЕЙДЖИ ---
    @staticmethod
    def status_macro(title: str, color: str = "Grey", subtle: bool = False) -> str:
        """
        color: Grey, Red, Yellow, Green, Blue
        subtle: True делает рамку тонкой
        """
        valid_colors = ["Grey", "Red", "Yellow", "Green", "Blue"]
        safe_color = color if color in valid_colors else "Grey"
        is_subtle = "true" if subtle else "false"

        return f"""
        <ac:structured-macro ac:name="status">
            <ac:parameter ac:name="title">{ConfluenceMarkup.escape(title)}</ac:parameter>
            <ac:parameter ac:name="colour">{safe_color}</ac:parameter>
            <ac:parameter ac:name="subtle">{is_subtle}</ac:parameter>
        </ac:structured-macro>
        """

    # --- CODE BLOCK ---
    @staticmethod
    def code_block(code: str, language: str = "json", title: str = None, collapse: bool = False) -> str:
        title_param = f'<ac:parameter ac:name="title">{ConfluenceMarkup.escape(title)}</ac:parameter>' if title else ""
        collapse_param = '<ac:parameter ac:name="collapse">true</ac:parameter>' if collapse else ""

        return f"""
        <ac:structured-macro ac:name="code">
            {title_param}
            <ac:parameter ac:name="language">{language}</ac:parameter>
            <ac:parameter ac:name="linenumbers">true</ac:parameter>
            {collapse_param}
            <ac:plain-text-body><![CDATA[{code}]]></ac:plain-text-body>
        </ac:structured-macro>
        """

    # --- MERMAID (Visual) ---
    @staticmethod
    def mermaid_macro(code: str, filename: str | None = None) -> str:
        """
        Генерирует макрос 'mermaidjs' специально для плагина от Stratus Add-ons.
        Этот плагин требует, чтобы код был внутри JSON объекта {"diagramDefinition": "..."}.
        """
        # 1. Формируем словарь, который ждет плагин
        data = {
            "diagramDefinition": code
        }

        # 2. Превращаем словарь в JSON-строку (это автоматически экранирует кавычки и переносы строк)
        json_body = json.dumps(data)

        # 3. Генерируем XML
        return f"""
            <ac:structured-macro ac:name="mermaidjs">
                <ac:parameter ac:name="theme">default</ac:parameter>
                <ac:parameter ac:name="version">2</ac:parameter>
                <ac:plain-text-body><![CDATA[{json_body}]]></ac:plain-text-body>
            </ac:structured-macro>
            """

    # --- ДАТА ---
    @staticmethod
    def time_macro(date_obj) -> str:
        if not date_obj:
            return ""
        date_str = date_obj.strftime("%Y-%m-%d")
        return f'<ac:structured-macro ac:name="time"><ac:parameter ac:name="datetime">{date_str}</ac:parameter></ac:structured-macro>'

    # --- LAYOUTS ---
    @staticmethod
    def layout_section(columns: List[str],
                       type: Literal["two_equal", "two_right_sidebar", "three_equal", "single"] = "two_equal") -> str:
        cells_html = ""
        for col_content in columns:
            cells_html += f'<ac:layout-cell>{col_content}</ac:layout-cell>'

        return f"""
            <ac:layout>
                <ac:layout-section ac:type="{type}">
                    {cells_html}
                </ac:layout-section>
            </ac:layout>
            """

    @staticmethod
    def expand_block(title: str, content: str) -> str:
        return f"""
            <ac:structured-macro ac:name="expand">
                <ac:parameter ac:name="title">{ConfluenceMarkup.escape(title)}</ac:parameter>
                <ac:rich-text-body>{content}</ac:rich-text-body>
            </ac:structured-macro>
            """

    @staticmethod
    def toc() -> str:
        return '<ac:structured-macro ac:name="toc" />'

    # --- ICONS ---
    @staticmethod
    def icon_check() -> str:
        return '<ac:emoticon ac:name="tick" ac:emoji-shortname=":check_mark:" ac:emoji-fallback="✅" />'

    @staticmethod
    def icon_cross() -> str:
        return '<ac:emoticon ac:name="cross" ac:emoji-shortname=":cross_mark:" ac:emoji-fallback="❌" />'

    @staticmethod
    def icon_star() -> str:
        return '<ac:emoticon ac:name="yellow-star" ac:emoji-shortname=":star:" ac:emoji-fallback="⭐" />'
