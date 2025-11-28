from app.models.dto import RequirementsDocument, RequirementItem
from backend_core import BusinessRequirements

def business_to_requirements_doc(br: dict) -> RequirementsDocument:
    # br — это dict от BusinessRequirements.model_dump()
    return RequirementsDocument(
        project_name=br.get("project_name", "New Project"),
        goal=br.get("goal", ""),
        scope=br.get("scope", []),
        stakeholders=br.get("stakeholders", []),
        # business_rules / kpi / requirements можно пока заполнять простыми значениями
        business_rules=br.get("missing_info", []),
        kpi=[],
        requirements=[],
    )
