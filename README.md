# AI Business Analyst Platform

An interactive platform that turns a **raw product idea** into a structured **Business Requirements Document (BRD)** through a conversation with an AI “Business Analyst”.

The system:

- guides the user through **goal, scope, stakeholders, business rules, KPIs** and more;
- keeps a **live BRD** updated in real time on the UI;
- uses a **multi-agent LLM workflow (4 collaborating agents)** to refine and validate the document;
- can **publish the final BRD to Confluence** in a ready-to-use format.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)  
2. [Tech Stack](#tech-stack)  
3. [Repository Structure](#repository-structure)  
4. [Getting Started](#getting-started)  
   - [Prerequisites](#prerequisites)  
   - [Backend Setup](#backend-setup)  
   - [Frontend Setup](#frontend-setup)  
   - [Docker (optional)](#docker-optional)  
5. [Environment Variables](#environment-variables)  
6. [Backend API](#backend-api)  
   - [GET /api/v1/health](#get-apiv1health)  
   - [POST /api/v1/chat](#post-apiv1chat)  
   - [POST /api/v1/preview](#post-apiv1preview)  
   - [POST /api/v1/publish](#post-apiv1publish)  
7. [LLM Workflow (Multi-Agent Design)](#llm-workflow-multiagent-design)  
8. [Development & Contributing](#development--contributing)  
9. [Future Improvements](#future-improvements)

---

## Architecture Overview

High-level flow:

1. **User** describes a product / system idea in the chat UI.
2. **Frontend** sends the message + chat history to `POST /api/v1/chat`.
3. **Backend (FastAPI)**:
   - converts history into LangChain messages,
   - passes state into a **LangGraph workflow** (`backend_core.py`),
   - runs a pipeline of **four LLM agents** (Critic, Interviewer, Architect, Writer),
   - incrementally updates a `RequirementsDocument` (BRD structure).
4. Backend returns:
   - `assistant_message` — AI reply for the chat,
   - `requirements` — structured BRD state,
   - `current_step` — where we are in the workflow,
   - `diagram_mermaid` — optional Mermaid diagram,
   - `final_report_html` — final Confluence-ready HTML.
5. On finalize, frontend can:
   - **preview** the BRD via `/api/v1/preview`,
   - **publish** it to Confluence via `/api/v1/publish`.

---

## Tech Stack

### Backend

- **Python 3.12**
- **FastAPI** — REST API
- **Uvicorn** — ASGI server
- **Pydantic v2** — data validation and DTOs
- **LangGraph** — multi-agent LLM workflow orchestrator
- **LangChain** — LLM messages and tools
- **OpenAI API** — LLM provider
- **Confluence API** — BRD publishing
- **Docker** — containerization (optional)

### Frontend

- **Next.js (App Router)**
- **React**
- **TypeScript**
- **shadcn/ui** — reusable components
- **Zustand** — lightweight state management for live BRD

---

## Repository Structure

> Folder names may differ slightly; adjust if needed.

```bash
.
├── backend/
│   ├── app/
│   │   ├── main.py                   # FastAPI entrypoint
│   │   ├── core/
│   │   │   ├── config.py             # Settings / env loading
│   │   │   └── logging.py            # Logger configuration
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── health.py         # GET /api/v1/health
│   │   │       ├── chat.py           # POST /api/v1/chat (LLM workflow)
│   │   │       ├── preview.py        # POST /api/v1/preview
│   │   │       └── publish.py        # POST /api/v1/publish (Confluence)
│   │   ├── models/
│   │   │   └── dto.py                # RequirementsDocument + DTOs
│   │   └── services/
│   │       ├── ai_engine.py          # Wrapper for LangGraph app
│   │       ├── confluence.py         # ConfluenceClient
│   │       └── confluence_generator/
│   │           └── renderer.py       # BRD → Confluence HTML/Storage
│   ├── backend_core.py               # LLM multi-agent workflow (LangGraph)
│   ├── prompts_config.py             # Prompt templates (if used separately)
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml            # (optional)
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   └── page.tsx              # Main page: chat + live BRD
    │   ├── components/
    │   │   ├── chat-interface.tsx    # Chat UI → calls /api/v1/chat
    │   │   └── live-document.tsx     # Right-hand live BRD viewer
    │   ├── lib/
    │   │   └── mapper.ts             # Map backend BRD → UI sections
    │   ├── store/
    │   │   └── ui-store.ts           # Zustand store for document state
    │   └── types/
    │        └── api.ts                # TypeScript types for backend API
    ├── package.json
    └── next.config.js
```
# Getting Started

## Prerequisites

- **Python:** 3.12+
- **Node.js:** 18+ (for Next.js)
- **Package Manager:** npm / pnpm / yarn
- **OpenAI API Key**
- **(Optional)** Confluence URL + API Token (for publishing)

## Backend Setup

### 1. Create and activate virtual environment  
*(optional, but recommended)*

```bash
cd backend
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```
### 2. Install dependencies

```bash
cd backend
pip install -r requirements.txt
```
### 3. Configure environment variables

Create a `.env` file inside the `backend/` directory.

Refer to the **Environment Variables** section for all required keys.

### 4. Run backend

```bash
uvicorn app.main:app --reload
```
## Backend will be available at:

- **Swagger UI:** http://127.0.0.1:8000/docs  
- **Health Check:** http://127.0.0.1:8000/api/v1/health

## Frontend Setup

### 1. Install dependencies

```bash
cd frontend
npm install
# or
pnpm install
# or
yarn
```
### 2. Configure environment variables

Create a `.env.local` file inside the `frontend/` directory with:

### 3. Run frontend dev server

```bash
npm run dev
# or
pnpm dev
# or
yarn dev
```
### Open the UI in your browser

👉 **http://localhost:3000**

You should see:

- **Left side:** chat with the AI Business Analyst  
- **Right side:** live BRD that updates as the conversation progresses

## Docker (Optional)

A minimal Docker setup for the backend:

```bash
cd backend
docker build -t ai-ba-backend .
docker run -p 8000:8000 --env-file .env ai-ba-backend
```
⚠️ **Important:** Ensure that `backend_core.py` and `prompts_config.py` are included in the Docker image by adding the following lines in your `Dockerfile`:

```dockerfile
COPY backend_core.py /app/backend_core.py
COPY prompts_config.py /app/prompts_config.py
```
## Environment Variables

### Backend `.env` (example)

```env
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini

# Confluence (optional, for publishing)
CONFLUENCE_URL=https://your.atlassian.net/wiki
CONFLUENCE_USERNAME=mail@domain.com
CONFLUENCE_API_TOKEN=your_confluence_api_token
CONFLUENCE_SPACE_KEY=SPACEKEY

# Logging
LOG_LEVEL=INFO
```
### Frontend `.env.local` (example)

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```
## Backend API

### `GET /api/v1/health`

Simple health check.

**Response example:**

```json
{
  "status": "ok",
  "version": "1.0.0"
}
```
### `POST /api/v1/chat`

Main AI endpoint used by the frontend chat UI to interact with the AI Business Analyst.

---

#### Request Body Example

```json
{
  "session_id": "session-123",
  "message": "We want to build a cashback system for retail clients",
  "history": [
    {
      "role": "assistant",
      "content": "Hi, I am your AI Business Analyst. What system are we designing?"
    }
  ],
  "requirements": null
}
```
**Field Explanation:**

- `session_id` — client-side session ID (string)  
- `message` — current user message  
- `history` — full conversation history (assistant + user), excluding current message  
- `requirements` — optional current BRD state (can be omitted; backend can rebuild from history)

**Response Example:**

```json
{
  "assistant_message": "Who will fund the cashback — only the bank, partners, or a mixed model?",
  "requirements": {
    "project_name": "Cashback System for Bank Clients",
    "goal": "Increase loyalty and activity via cashback on card and partner operations.",
    "scope": [
      "Rule engine for multiple loyalty programs",
      "Cashback accrual for card transactions and services",
      "Differentiated rates by category and client segment",
      "Limits and caps per client/product/program",
      "Manual adjustments with 4-eyes approval",
      "Integration with Core banking, ESB, Kafka",
      "Admin portal for programs, rules, partners",
      "Analytics and export to DWH"
    ],
    "stakeholders": [
      "Head of Retail Banking",
      "Head of Digital",
      "Marketing",
      "Risk Management",
      "Finance",
      "IT",
      "InfoSec",
      "Contact Center"
    ],
    "business_rules": [
      "Clarify which transaction types are eligible for cashback.",
      "Define target model: cash, points, or mixed, and usage scenarios.",
      "Specify expected load: active clients, daily tx volume, latency requirements."
    ],
    "kpi": [],
    "requirements": [],
    "diagram_mermaid": null,
    "version": "1.0.0",
    "document_status": "DRAFT",
    "author": "AI Business Analyst",
    "updated_at": "2025-11-28T11:29:26.197380"
  },
  "current_step": "rules",
  "is_completed": false,
  "diagram_mermaid": null,
  "final_report_html": null
}
```
**Key Fields:**

- `assistant_message` — text reply to show in chat  
- `requirements` — structured BRD (`RequirementsDocument`)  
- `current_step` — current workflow step (e.g., `intro`, `goal`, `scope`, `stakeholders`, `rules`, `kpi`, `final`)  
- `is_completed` — becomes `true` once the Writer agent finalizes the BRD  
- `diagram_mermaid` — optional Mermaid diagram code  
- `final_report_html` — final BRD in Confluence-ready HTML


### `POST /api/v1/preview`

Render the current BRD into HTML for preview.

---

#### Request Body Example

```json
{
  "document": {
    "project_name": "Cashback System for Bank Clients",
    "goal": "...",
    "scope": ["..."],
    "stakeholders": ["..."],
    "business_rules": ["..."],
    "kpi": [],
    "requirements": [],
    "diagram_mermaid": null,
    "version": "1.0.0",
    "document_status": "DRAFT",
    "author": "AI Business Analyst",
    "updated_at": "2025-11-28T11:29:26.197380"
  }
}
```
**Response Example:**

```json
{
  "html": "<h1>Business Requirements Document</h1>..."
}
```
Use this HTML in the frontend (modal or preview page) before publishing.

### `POST /api/v1/publish`

Publish the BRD to Confluence.

---

#### Request Body

Uses the same `RequirementsDocument` structure as in `/api/v1/preview`.

---

#### Response Example

```json
{
  "status": "created",
  "page_id": "123456789",
  "url": "https://your-domain.atlassian.net/wiki/spaces/SPACEKEY/pages/123456789/..."
}
```
## LLM Workflow (Multi-Agent Design)

The AI core is implemented in: backend/backend_core.py

It uses **LangGraph** to orchestrate a multi-step workflow over a shared state called `TribunalState`.

## State (`TribunalState`)

**Key Fields:**

- `messages` — LangChain chat history (Human + AI)  
- `requirements` — `BusinessRequirements` Pydantic model  
- `final_report_html` — final BRD HTML  
- `diagram_code` — Mermaid diagram  
- `integration_status` — technical status / metadata  

---

## Agents

The workflow uses four collaborating LLM agents:

### 🔍 Critic Agent (`critic_node`)
- Reviews collected information  
- Detects inconsistencies and contradictions  
- Identifies gaps and missing requirements  
- Suggests what must be clarified before finalizing  

### ❓ Interviewer Agent (`interviewer_node`)
- Asks targeted follow-up questions to the user  
- Focuses on constraints, priorities, and edge cases  
- Ensures enough business context for a meaningful BRD  

### 🏗️ Architect Agent (`architect_node`)
- Adds system-level details and integrations  
- Proposes high-level architecture and flows  
- Integrates with systems like Core banking, ESB, Kafka, frontends  
- Extends requirements with NFRs and technical aspects  

### ✍️ Writer Agent (`writer_node`)
- Produces the final BRD  
- Generates structured sections:
  - Goal, Scope, Stakeholders  
  - Business Rules, KPIs  
  - Functional/Non-functional requirements  
- Outputs Confluence-ready HTML (`final_report_html`)  
- May generate Mermaid diagram (`diagram_code`)  
- Ensures clarity, consistency, and readability

## LangGraph Orchestration

Simplified workflow sketch:

```python
from langgraph.graph import StateGraph
from .state import TribunalState
from .nodes import critic_node, interviewer_node, architect_node, writer_node

# Initialize workflow graph with shared state
workflow = StateGraph(TribunalState)

# Add agents as nodes
workflow.add_node("critic", critic_node)
workflow.add_node("interviewer", interviewer_node)
workflow.add_node("architect", architect_node)
workflow.add_node("writer", writer_node)

# Add edges / routing logic...
# workflow.add_edge("critic", "interviewer")
# ...

# Compile the workflow
app = workflow.compile()
```
## FastAPI Integration

Example of invoking the AI workflow in FastAPI:

```python
from app.services.ai_engine import run_ai_step

ai_state = run_ai_step(
    history=history_dicts,
    user_message=request.message,
    requirements=request.requirements or {},
)
```
## Development & Contributing

### Typical Development Loop

1. Run backend and frontend locally.  
2. Open [http://localhost:3000](http://localhost:3000) and interact with the AI.  
3. Watch live BRD updates on the right panel.  

**If behavior is not ideal:**

- Tune prompts and transitions in `backend/backend_core.py`  
- Update mapping logic in `frontend/src/lib/mapper.ts`  
- Adjust TypeScript types in `frontend/src/types/api.ts`  

---

### Ideas for Contributions

- Better prompt engineering for each agent  
- Additional document templates: BRD, SRS, API Spec, technical design docs  
- Improved analytics / logging of AI interactions  
- Support multiple languages (RU / EN / KZ)  
- UI to visualize workflow steps and agent decisions

## Future Improvements

- **Session persistence** — store BRD and chat history in a database  
- **Authentication & roles** — associate sessions with users/teams  
- **Export formats** — PDF, Word, Markdown  
- **Template library** — pick BRD, SRS, “Discovery Doc”, etc.  
- **More specialized agents:**  
  - Risk Analyst  
  - Non-Functional Requirements Expert  
  - Data Architect


## Contacts

If you have questions, ideas, or want to contribute, feel free to reach out:
 
- **Email:** mogleg2@gmail.com
- **Telegram:** https://t.me/makymt
