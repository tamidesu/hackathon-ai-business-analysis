// src/lib/mapper.ts
import { BackendRequirements, DocumentSection } from "@/types/api";

export function mapBackendDocToSections(req: BackendRequirements): DocumentSection[] {
    // Превращаем списки требований в Markdown-списки
    const funcReqs = req.functional_requirements
        .map(r => `* ${r}`)
        .join("\n");

    const nonFuncReqs = req.non_functional_requirements
        .map(r => `* ${r}`)
        .join("\n");

    return [
        {
            id: "goal",
            title: "Бизнес-цель",
            content: req.business_goal
        },
        {
            id: "scope",
            title: "Границы решения (Scope)",
            content: req.solution_scope
        },
        {
            id: "func",
            title: "Функциональные требования",
            content: funcReqs
        },
        {
            id: "non-func",
            title: "Нефункциональные требования",
            content: nonFuncReqs
        }
    ];
}