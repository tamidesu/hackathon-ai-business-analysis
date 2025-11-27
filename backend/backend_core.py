import os
import re
import operator
from typing import Annotated, List, TypedDict, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langgraph.graph import StateGraph, END

# --- 1. CONFIGURATION ---
load_dotenv()
if not os.getenv("OPENAI_API_KEY") and "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "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"

# --- MODEL SELECTION ---
model_brain_name = "gpt-5.1"      
model_fast_name = "gpt-5-mini"    

try:
    llm_brain = ChatOpenAI(model=model_brain_name, temperature=0.4) 
    llm_fast = ChatOpenAI(model=model_fast_name, temperature=0.5)
except Exception:
    print(f"⚠️ Models {model_brain_name}/{model_fast_name} not found. Using Fallback.")
    llm_brain = ChatOpenAI(model="gpt-4o", temperature=0.4)
    llm_fast = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)

# --- 2. KNOWLEDGE BASE (RAG) ---
class ForteKnowledgeBase:
    @staticmethod
    def get_tech_stack() -> str:
        return """
        FORTEBANK ENTERPRISE STACK:
        - Core: Colvir (АБС) via IBM App Connect (ESB).
        - Auth: Keycloak (SSO, OIDC).
        - Front: Flutter (Mobile), React (Web), Forte UI Kit v3.
        - Data: Oracle Exadata, Kafka.
        - Security: WAF, SIEM, DLP.
        """
    
    @staticmethod
    def get_compliance_rules() -> str:
        return "COMPLIANCE: 152-ФЗ, PCI DSS, OWASP Top 10."

# --- 3. DATA MODELS ---
class UserStory(BaseModel):
    role: str = Field(description="Роль (на русском)")
    action: str = Field(description="Действие (на русском)")
    value: str = Field(description="Ценность (на русском)")

class BusinessRequirements(BaseModel):
    project_name: str = Field(description="Название проекта", default="Новый проект")
    goal: str = Field(description="Бизнес-цель", default="")
    stakeholders: List[str] = Field(description="Роли", default=[])
    scope: List[str] = Field(description="Функции", default=[])
    suggested_modules: List[str] = Field(description="Предложенные модули", default=[])
    user_stories: List[UserStory] = Field(description="User Stories", default=[])
    missing_info: List[str] = Field(description="Чего не хватает", default=[])
    recommendations: List[str] = Field(description="Советы пользователю: что добавить в запрос, чтобы результат был лучше", default=[])

# --- 4. SYSTEM PROMPTS (RUSSIAN ENTERPRISE) ---

PROMPT_CRITIC = f"""
Ты — Системный Архитектор (Big 4).
Твоя задача — формализовать идею в требования.

КОНТЕКСТ: {ForteKnowledgeBase.get_tech_stack()}

ПРАВИЛА (СТРОГО РУССКИЙ ЯЗЫК):
1. **Анализ:** Если пользователь пишет коротко, ты расширяешь требования.
   - *Вход:* "Хочу игру".
   - *Выход:* Scope = ["Геймификация", "Профиль игрока", "Магазин наград", "Лидерборд"].
2. **User Stories:** Создавай истории на русском: "Как [Роль], я хочу [Действие], чтобы [Ценность]".
3. **Модули:** Всегда предлагай: "Панель администратора", "Логирование", "Аналитика".
4. **Рекомендации (ВАЖНО):** В поле `recommendations` дай 3-5 конкретных советов пользователю, что еще можно уточнить.
   - Пример: "Укажите предполагаемую нагрузку (RPS)", "Нужна ли интеграция с картами?", "Кто будет администрировать систему?".

ВЫВОД: JSON.
"""

PROMPT_INTERVIEWER = """
Ты — Product Owner.
Твоя цель — уточнить детали на РУССКОМ языке.

АЛГОРИТМ:
1. Если JSON пустой — спроси суть продукта.
2. Если есть суть — спроси про монетизацию или пользователей.
3. Не задавай больше 1 вопроса за раз.
"""

# --- PROMPT для диаграммы ---
PROMPT_ARCHITECT = """
Ты — Solution Architect.
Нарисуй **System Context Diagram** (Mermaid graph LR).

ГЛАВНАЯ ЦЕЛЬ: Избежать "эффекта спагетти" (пересекающихся линий).

ПРАВИЛА ВИЗУАЛИЗАЦИИ:
1. **Ориентация:** `graph LR` (Слева -> Направо).
2. **Порядок потока данных:** - Слева: `subgraph Client`
   - Центр-Слева: `subgraph Gateway`
   - Центр: `subgraph Core`
   - Справа: `subgraph External`
3. **Стили:**
   - Определи классы:
     `classDef client fill:#e3f2fd,stroke:#1565c0;`
     `classDef core fill:#e8f5e9,stroke:#2e7d32;`
     `classDef external fill:#fff3e0,stroke:#ef6c00;`
4. **Синтаксис (ВАЖНО):**
   - Каждая команда на **НОВОЙ СТРОКЕ**.
   - Используй **основное направление связей** (Client --> Gateway --> Core --> External).
   - Избегай циклических зависимостей, где это возможно.
   - ID узлов: латиница (n_app). Текст: Русский ["Приложение"].

ПРИМЕР СТРУКТУРЫ (СЛЕДУЙ ЕМУ):
graph LR
  classDef client fill:#e3f2fd,stroke:#1565c0;
  classDef core fill:#e8f5e9,stroke:#2e7d32;
  
  subgraph Client ["Клиент (Слева)"]
    direction TB
    n_app["Приложение"]
  end
  
  subgraph Core ["Ядро (Центр)"]
    direction TB
    n_api["API"]
  end
  
  n_app --> n_api
  class n_app client;
  class n_api core;
"""

PROMPT_WRITER = f"""
Ты — Lead Technical Writer.
Напиши **Детальный BRD** (Business Requirements Document) на **РУССКОМ ЯЗЫКЕ**.

ВХОДНЫЕ ДАННЫЕ: JSON.
ТЕХНОЛОГИИ: {ForteKnowledgeBase.get_tech_stack()}

ИНСТРУКЦИЯ (HTML):
1. **Объем:** Пиши подробно. Разворачивай каждый пункт в абзац текста. Не экономь слова.
2. **Структура документа:**
   - **Введение:** Описание проблемы и решения.
   - **Архитектура:** Опиши интеграцию с Colvir/IBM ESB.
   - **Функциональные требования:** Подробный список функций.
   - **User Stories:** Таблица.
   - **NFR (Нефункциональные требования):** Безопасность, SLA 99.9%, Нагрузка.
   - **Риски:** Опиши риски.
   
3. **Оформление:**
   - Используй CSS для красоты.
   - Заголовки H2 цветом #004d40.
   - Таблицы с границами.
"""

# --- 5. UTILS (FIXED SYNTAX) ---
class ConfluenceAdapter:
    @staticmethod
    def validate_and_prepare(html: str, title: str) -> dict:
        return {"status": "ready", "link": f"https://wiki.forte.kz/{title}"}

def clean_mermaid(code: str) -> str:
    """
    Безопасная очистка кода.
    Добавлена очистка неразрывных пробелов (0xa0), которые ломают парсер.
    """
    # Удаляем маркдаун
    clean = code.replace("```mermaid", "").replace("```", "").strip()
    
    # ВАЖНО: Удаляем неразрывные пробелы и прочий мусор
    clean = clean.replace("\u00a0", " ")
    
    # Фолбек: Разделение строк если модель выдала сплошной текст
    if "\n" not in clean and ";" not in clean:
        clean = clean.replace("graph LR", "graph LR\n")\
                     .replace("graph TD", "graph TD\n")\
                     .replace(" subgraph ", "\nsubgraph ")\
                     .replace(" end ", "\nend\n")\
                     .replace("-->", "--> ")\
                     .replace("  ", "\n")\
                     .replace(" classDef ", "\nclassDef ")\
                     .replace(" class ", "\nclass ")\
                     .replace(" direction ", "\ndirection ") 
    
    return clean

# --- 6. NODES ---
class TribunalState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    requirements: dict
    final_report_html: Optional[str]
    diagram_code: Optional[str]
    integration_status: Optional[dict]

def critic_node(state: TribunalState):
    try:
        structured = llm_brain.with_structured_output(BusinessRequirements)
        reqs = structured.invoke([SystemMessage(content=PROMPT_CRITIC)] + state['messages'])
        return {"requirements": reqs.model_dump()}
    except:
        return {"requirements": state.get('requirements', {})}

def interviewer_node(state: TribunalState):
    reqs = state['requirements']
    msg = f"{PROMPT_INTERVIEWER}\nДАННЫЕ: {reqs}"
    res = llm_fast.invoke([SystemMessage(content=msg)] + state['messages'])
    return {"messages": [res]}

def architect_node(state: TribunalState):
    reqs = state['requirements']
    res = llm_fast.invoke([HumanMessage(content=f"{PROMPT_ARCHITECT}\nDATA: {reqs}")])
    return {"diagram_code": clean_mermaid(res.content)}

def writer_node(state: TribunalState):
    reqs = state['requirements']
    res = llm_brain.invoke([HumanMessage(content=f"{PROMPT_WRITER}\nDATA: {reqs}")])
    html = res.content.replace("```html", "").replace("```", "").strip()
    status = ConfluenceAdapter.validate_and_prepare(html, reqs.get('project_name'))
    return {"final_report_html": html, "integration_status": status, "messages": [AIMessage(content="Документация готова.")]}

def router(state: TribunalState):
    reqs = state.get('requirements', {})
    msg = state['messages'][-1].content.lower()
    ready = reqs.get('goal')
    agreed = any(x in msg for x in ["да", "генер", "отчет", "тз", "составь"])
    return "architect" if (ready and agreed) else "interviewer"

# --- 7. COMPILE ---
workflow = StateGraph(TribunalState)
workflow.add_node("critic", critic_node)
workflow.add_node("interviewer", interviewer_node)
workflow.add_node("architect", architect_node)
workflow.add_node("writer", writer_node)

workflow.set_entry_point("critic")
workflow.add_conditional_edges("critic", router, {"interviewer": "interviewer", "architect": "architect"})
workflow.add_edge("interviewer", END)
workflow.add_edge("architect", "writer")
workflow.add_edge("writer", END)

app = workflow.compile()