import streamlit as st
import streamlit.components.v1 as components
import json
import os
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

# --- ИМПОРТ ---
try:
    from backend_core import app as backend_app
except ImportError as e:
    st.error(f"Error: {e}")
    st.stop()

st.set_page_config(layout="wide", page_title="Forte AI Analyst", page_icon="🏦")

# --- СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fff; }
</style>
""", unsafe_allow_html=True)

# --- ФУНКЦИИ СОХРАНЕНИЯ ---
HISTORY_FILE = "session_history.json"

def save_chat():
    data = {
        "messages": [{"type": m.type, "content": m.content} for m in st.session_state.messages],
        "requirements": st.session_state.requirements,
        "diagram": st.session_state.diagram_code,
        "report": st.session_state.final_report
    }
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    st.toast("✅ Чат сохранен!", icon="💾")

def load_chat():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        loaded_msgs = []
        for m in data["messages"]:
            if m["type"] == "human": loaded_msgs.append(HumanMessage(content=m["content"]))
            elif m["type"] == "ai": loaded_msgs.append(AIMessage(content=m["content"]))
        st.session_state.messages = loaded_msgs
        st.session_state.requirements = data.get("requirements", {})
        st.session_state.diagram_code = data.get("diagram")
        st.session_state.final_report = data.get("report")
        st.rerun()

def reset_session():
    st.session_state.messages = [AIMessage(content="Я готов к работе. Какую систему проектируем?")]
    st.session_state.requirements = {}
    st.session_state.final_report = None
    st.session_state.diagram_code = None
    st.rerun()

# --- ИНИЦИАЛИЗАЦИЯ ---
if "messages" not in st.session_state:
    st.session_state.messages = [AIMessage(content="Я готов к работе. Какую систему проектируем?")]
if "requirements" not in st.session_state: st.session_state.requirements = {}
if "final_report" not in st.session_state: st.session_state.final_report = None
if "diagram_code" not in st.session_state: st.session_state.diagram_code = None

# --- САЙДБАР ---
with st.sidebar:
    st.header("Управление")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        if st.button("💾 Save"): save_chat()
    with col_s2:
        if st.button("📂 Load"): load_chat()
    st.divider()
    if st.button("🗑️ Сброс (Новый чат)", type="primary"):
        reset_session()

# --- UI ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("💬 Диалог")
    container = st.container(height=600)
    for m in st.session_state.messages:
        role = "user" if isinstance(m, HumanMessage) else "assistant"
        container.chat_message(role).write(m.content)

    if prompt := st.chat_input("Ваш ответ..."):
        st.session_state.messages.append(HumanMessage(content=prompt))
        container.chat_message("user").write(prompt)
        
        with st.spinner("Анализ требований..."):
            try:
                res = backend_app.invoke({
                    "messages": st.session_state.messages, 
                    "requirements": st.session_state.requirements
                })
                st.session_state.messages.append(res['messages'][-1])
                st.session_state.requirements = res.get('requirements', {})
                if res.get('final_report_html'):
                    st.session_state.final_report = res['final_report_html']
                    st.session_state.diagram_code = res.get('diagram_code')
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    st.subheader("🧠 Артефакты")
    tab1, tab2, tab3 = st.tabs(["JSON", "Diagram", "Report"])
    
    with tab1:
        st.json(st.session_state.requirements, expanded=True)
    
    with tab2:
        if st.session_state.diagram_code:
            # --- ОБНОВЛЕННЫЙ РЕНДЕР MERMAID v10 (ESM) ---
            # Мы используем современный модульный импорт, который решает большинство
            # проблем с синтаксисом (direction TB, новые типы стрелок).
            mermaid_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ background-color: white; margin: 0; padding: 20px; font-family: sans-serif; }}
                    .mermaid {{ width: 100%; display: flex; justify-content: center; }}
                    #error-container {{ 
                        color: #D8000C; 
                        background-color: #FFBABA;
                        border: 1px solid #D8000C;
                        padding: 10px;
                        margin-top: 20px; 
                        display: none;
                        border-radius: 5px;
                        font-family: monospace;
                        white-space: pre-wrap;
                    }}
                </style>
            </head>
            <body>
                <div class="mermaid">
                {st.session_state.diagram_code}
                </div>
                
                <div id="error-container"></div>

                <script type="module">
                    // Используем ESM сборку Mermaid v10
                    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
                    
                    mermaid.initialize({{
                        startOnLoad: false,
                        theme: 'base',
                        securityLevel: 'loose',
                        themeVariables: {{
                            primaryColor: '#ffffff',
                            lineColor: '#333333',
                            fontSize: '16px'
                        }}
                    }});

                    // Запуск рендера
                    try {{
                        await mermaid.run({{
                            nodes: document.querySelectorAll('.mermaid')
                        }});
                    }} catch(e) {{
                        const errDiv = document.getElementById("error-container");
                        errDiv.style.display = "block";
                        errDiv.innerText = "Mermaid Error:\\n" + e.message;
                    }}
                </script>
            </body>
            </html>
            """
            components.html(mermaid_html, height=600, scrolling=True)
            with st.expander("Код диаграммы (для отладки)"):
                st.code(st.session_state.diagram_code, language="mermaid")
        else:
            st.info("Диаграмма будет здесь.")
            
    with tab3:
        if st.session_state.final_report:
            components.html(st.session_state.final_report, height=600, scrolling=True)
            st.download_button("Скачать BRD", st.session_state.final_report, "brd.html")
        else:
            st.info("Отчет будет здесь.")