export interface ChatRequest {
    session_id: string;
    message: string;
}

export interface BackendRequirements {
    project_name: string;
    version: string;
    document_status: string;
    last_updated: string;
    business_goal: string;
    solution_scope: string;
    functional_requirements: string[];
    non_functional_requirements: string[];
    diagram_mermaid: string;
}

export interface ChatResponse {
    assistant_message: string;
    requirements?: BackendRequirements; // Может не быть, если это просто болтовня
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