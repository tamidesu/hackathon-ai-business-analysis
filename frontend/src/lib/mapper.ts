// src/lib/mapper.ts
import { BackendRequirements, DocumentSection } from "@/types/api";

const formatList = (items?: string[]): string =>
  items && items.length
    ? items.map((r) => `* ${r}`).join("\n")
    : "_Не указано_";

export function mapBackendDocToSections(req: BackendRequirements): DocumentSection[] {
  const sections: DocumentSection[] = [
    {
      id: "goal",
      title: "Цель проекта",
      content: req.goal || "_Не указана_",
    },
    {
      id: "scope",
      title: "Границы решения (Scope)",
      content: req.scope && req.scope.length
        ? req.scope.map((item) => `* ${item}`).join("\n")
        : "_Не указано_",
    },
    {
      id: "stakeholders",
      title: "Заинтересованные стороны",
      content: req.stakeholders && req.stakeholders.length
        ? req.stakeholders.map((s) => `* ${s}`).join("\n")
        : "_Не указано_",
    },
    {
      id: "rules",
      title: "Бизнес-правила и допущения",
      content: formatList(req.business_rules),
    },
  ];

  if (req.kpi && req.kpi.length > 0) {
    sections.push({
      id: "kpi",
      title: "KPI и метрики успеха",
      content: formatList(req.kpi),
    });
  }

  if (req.requirements && req.requirements.length > 0) {
    const reqContent = req.requirements
      .map(
        (r) =>
          `* **${r.id} – ${r.title}**\n  - Приоритет: ${r.priority}\n  - Статус: ${r.status}\n  - Описание: ${r.description}`,
      )
      .join("\n\n");

    sections.push({
      id: "requirements",
      title: "Функциональные требования",
      content: reqContent,
    });
  }

  return sections;
}
