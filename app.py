import streamlit as st

from src.sample_database import create_sample_database
from src.sql_rag_agent import SQLRAGAssistant


st.set_page_config(
    page_title="RAG NLP SQL",
    page_icon=":bar_chart:",
    layout="wide",
)


def inject_styles():
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top right, rgba(20,184,166,0.16), transparent 28%),
                    radial-gradient(circle at top left, rgba(56,189,248,0.14), transparent 24%),
                    #0b1020;
            }
            .hero-card {
                background: linear-gradient(135deg, rgba(15,23,42,0.96), rgba(17,24,39,0.92));
                border: 1px solid rgba(148,163,184,0.22);
                border-radius: 22px;
                padding: 1.4rem 1.5rem;
                box-shadow: 0 18px 60px rgba(2,6,23,0.34);
                margin-bottom: 1rem;
            }
            .hero-title {
                font-size: 3rem;
                font-weight: 800;
                line-height: 1;
                margin: 0 0 0.6rem 0;
                color: #f8fafc;
                letter-spacing: -0.04em;
            }
            .hero-subtitle {
                color: #cbd5e1;
                font-size: 1.02rem;
                margin-bottom: 1rem;
            }
            .chip-row {
                display: flex;
                gap: 0.6rem;
                flex-wrap: wrap;
                margin-top: 0.7rem;
            }
            .chip {
                background: rgba(15,118,110,0.16);
                color: #ccfbf1;
                border: 1px solid rgba(45,212,191,0.25);
                border-radius: 999px;
                padding: 0.35rem 0.75rem;
                font-size: 0.88rem;
            }
            .info-grid {
                display: grid;
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.9rem;
                margin: 0.4rem 0 1.2rem 0;
            }
            .info-card {
                background: rgba(15,23,42,0.82);
                border: 1px solid rgba(148,163,184,0.18);
                border-radius: 18px;
                padding: 1rem;
            }
            .info-card-title {
                color: #f8fafc;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }
            .info-card-text {
                color: #cbd5e1;
                font-size: 0.93rem;
                line-height: 1.45;
            }
            .example-box {
                background: rgba(15,23,42,0.76);
                border: 1px solid rgba(148,163,184,0.18);
                border-radius: 18px;
                padding: 1rem 1rem 0.2rem 1rem;
                margin-bottom: 1rem;
            }
            div[data-testid="stChatMessage"] {
                border-radius: 20px;
                border: 1px solid rgba(148,163,184,0.14);
                background: rgba(15,23,42,0.72);
                padding: 0.3rem 0.25rem;
                box-shadow: 0 10px 30px rgba(2,6,23,0.22);
            }
            div[data-testid="stExpander"] {
                border-radius: 16px;
                overflow: hidden;
                border: 1px solid rgba(148,163,184,0.18);
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


EXAMPLE_QUESTIONS = [
    "Quais sao as tabelas do banco de dados?",
    "Qual a receita por segmento de cliente?",
    "Quais produtos geraram mais receita?",
    "Quantos pedidos pendentes existem?",
    "Quais sao os pedidos pagos mais recentes?",
]


def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Olá! Eu posso responder perguntas em linguagem natural sobre um banco SQL "
                    "de vendas B2B, com clientes, produtos, pedidos, itens de pedido e receita."
                ),
            }
        ]
    if "assistant" not in st.session_state:
        create_sample_database()
        st.session_state.assistant = SQLRAGAssistant(top_k=5, verbose=False)
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = None


def render_header():
    st.markdown(
        """
        <div class="hero-card">
            <div class="hero-title">RAG NLP SQL</div>
            <div class="hero-subtitle">
                Assistente SQL em linguagem natural para um banco fictício de vendas B2B,
                com recuperação de contexto, consultas estruturadas e respostas explicativas.
            </div>
            <div class="chip-row">
                <span class="chip">LangChain</span>
                <span class="chip">SQLite</span>
                <span class="chip">RAG de schema</span>
                <span class="chip">Streamlit</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="info-grid">
            <div class="info-card">
                <div class="info-card-title">Sobre a base</div>
                <div class="info-card-text">
                    O banco representa uma operação B2B com clientes, produtos, pedidos,
                    itens de pedido e receita.
                </div>
            </div>
            <div class="info-card">
                <div class="info-card-title">Como o RAG ajuda</div>
                <div class="info-card-text">
                    O retrieval recupera contexto sobre tabelas, joins e regras de negócio
                    antes da geração do SQL.
                </div>
            </div>
            <div class="info-card">
                <div class="info-card-title">Modo atual</div>
                <div class="info-card-text">
                    Sem OPENAI_API_KEY o app entra em modo demo, mas continua útil para
                    testar perguntas-chave e a UX do projeto.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_examples():
    st.markdown('<div class="example-box">', unsafe_allow_html=True)
    st.markdown("**Perguntas de exemplo**")
    cols = st.columns(len(EXAMPLE_QUESTIONS))
    for idx, question in enumerate(EXAMPLE_QUESTIONS):
        if cols[idx].button(question, key=f"example_{idx}", use_container_width=True):
            st.session_state.pending_prompt = question
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    inject_styles()
    init_state()
    render_header()
    render_examples()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("context"):
                with st.expander("Contexto recuperado"):
                    for item in message["context"]:
                        st.write(f"- {item}")

    prompt = st.chat_input("Pergunte sobre receita, clientes, segmentos, produtos ou pedidos")
    if not prompt and st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consultando o banco de dados..."):
                result = st.session_state.assistant.ask(prompt)
                context_items = [doc.page_content for doc in result["retrieved_context"]]
                st.markdown(result["answer"])
                with st.expander("Contexto recuperado"):
                    for item in context_items:
                        st.write(f"- {item}")

        st.session_state.messages.append(
            {"role": "assistant", "content": result["answer"], "context": context_items}
        )


if __name__ == "__main__":
    main()
