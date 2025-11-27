from .markup import ConfluenceMarkup as CM


def render_mermaid_section(title: str, code: str, filename: str | None = None) -> str:
    visual = CM.mermaid_macro(code, filename=filename)
    code_block = CM.code_block(code, language="mermaid", title="Mermaid Source", collapse=True)

    return f"""
    <h2>📊 {CM.escape(title)}</h2>
    <p>{visual}</p>
    {CM.expand_block("Show Mermaid Source Code", code_block)}
    """
