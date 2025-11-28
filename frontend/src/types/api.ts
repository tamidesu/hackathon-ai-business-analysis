// src/types/api.ts

// Сообщение чата, которое мы шлём на бэкенд
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  history?: ChatMessage[];
  // на будущее — можно передавать накопленные требования,
  // сейчас можно не использовать
  requirements?: BackendRequirements | null;
}

// Один Requirement из backend (RequirementItem)
export interface BackendRequirementItem {
  id: string;
  title: string;
  description: string;
  priority: string; // High/Medium/Low
  status: string;   // Draft/Approved/etc
}

// Это 1:1 с твоим Python RequirementsDocument
export interface BackendRequirements {
  project_name: string;
  goal: string;
  scope: string[];
  stakeholders: string[];
  business_rules: string[];
  kpi: string[];
  requirements: BackendRequirementItem[];
  diagram_mermaid?: string | null;

  version: string;
  document_status: string;
  author: string;
  updated_at: string; // datetime из Python приходит строкой
}

export type CurrentStep =
  | "intro"
  | "goal"
  | "scope"
  | "stakeholders"
  | "rules"
  | "kpi"
  | "flows"
  | "constraints"
  | "final";

export interface ChatResponse {
  assistant_message: string;
  requirements?: BackendRequirements; // может не быть в болтовне
  current_step: CurrentStep;
  is_completed: boolean;
  diagram_mermaid?: string | null;
  final_report_html?: string | null;
}

export interface DocumentSection {
  id: string;
  title: string;
  content: string;
}

export interface Artifacts {
  docTitle: string;
  docVersion: string;
  sections: DocumentSection[];
  diagramCode: string;
}


type PublishResponse = {
  confluence_url: string;
  page_id: string;
  status: string; // "created" | "updated"
};