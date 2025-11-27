# app/services/requirements.py
from app.models.dto import RequirementsDocument


def render_confluence_storage(doc: RequirementsDocument) -> str:
    """
    Генерирует HTML в формате Confluence Storage.
    Используем базовые макросы: TOC, info, expand.
    """

    requirements_rows = "".join(
        f"""
        <tr>
          <td>{req.id}</td>
          <td>{req.title}</td>
          <td>{req.description}</td>
          <td>{req.priority}</td>
          <td>{req.status}</td>
        </tr>
        """
        for req in doc.requirements
    )

    scope_list = "".join(f"<li>{item}</li>" for item in doc.scope)
    stakeholders_list = "".join(f"<li>{item}</li>" for item in doc.stakeholders)
    rules_list = "".join(f"<li>{item}</li>" for item in doc.business_rules)
    kpi_list = "".join(f"<li>{item}</li>" for item in doc.kpi)

    html = f"""
<h1>BRD: {doc.project_name}</h1>

<!-- TOC макрос -->
<ac:structured-macro ac:name="toc">
  <ac:parameter ac:name="minLevel">1</ac:parameter>
  <ac:parameter ac:name="maxLevel">3</ac:parameter>
  <ac:parameter ac:name="type">list</ac:parameter>
  <ac:parameter ac:name="outline">true</ac:parameter>
  <ac:rich-text-body/>
</ac:structured-macro>

<h2>1. Goal</h2>

<ac:structured-macro ac:name="info">
  <ac:rich-text-body>
    <p>{doc.goal}</p>
  </ac:rich-text-body>
</ac:structured-macro>

<h2>2. Scope</h2>
<ul>
  {scope_list}
</ul>

<h2>3. Stakeholders</h2>
<ul>
  {stakeholders_list}
</ul>

<h2>4. Business Rules</h2>

<ac:structured-macro ac:name="expand">
  <ac:parameter ac:name="title">Показать бизнес-правила</ac:parameter>
  <ac:rich-text-body>
    <ul>
      {rules_list}
    </ul>
  </ac:rich-text-body>
</ac:structured-macro>

<h2>5. KPI</h2>
<ul>
  {kpi_list}
</ul>

<h2>6. Requirements</h2>
<table>
  <tbody>
    <tr>
      <th>ID</th>
      <th>Title</th>
      <th>Description</th>
      <th>Priority</th>
      <th>Status</th>
    </tr>
    {requirements_rows}
  </tbody>
</table>
"""
    return html
