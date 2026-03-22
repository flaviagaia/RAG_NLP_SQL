import sqlite3

from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.retrievers import BM25Retriever
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI

from .config import DB_PATH, load_settings
from .rag_context import build_context_documents


SYSTEM_PREFIX_TEMPLATE = """
You are an analytics assistant that answers business questions with SQL.

Retrieved business context:
{rag_context}

Rules:
- Always inspect the available tables before answering if the question is ambiguous.
- Generate syntactically correct SQL for {dialect}.
- Unless the user asks for all rows, limit the output to at most {top_k} rows.
- Prefer explicit joins over implicit joins.
- Explain the result in plain language after querying.
- Never invent columns or tables.
- If the question cannot be answered from the database, say so clearly.
"""


class SQLRAGAssistant:
    def __init__(self, top_k: int = 5, verbose: bool = False):
        settings = load_settings()
        self.top_k = top_k
        self.verbose = verbose
        self.demo_mode = not bool(settings["openai_api_key"])
        self.retriever = BM25Retriever.from_documents(build_context_documents())
        self.retriever.k = 3
        self.db = SQLDatabase.from_uri(settings["database_uri"])
        self.llm = None
        if not self.demo_mode:
            self.llm = ChatOpenAI(
                model=settings["openai_model"],
                api_key=settings["openai_api_key"],
                temperature=0,
            )

    def ask(self, question: str):
        retrieved_docs = self.retriever.invoke(question)
        if self.demo_mode:
            answer = self._answer_in_demo_mode(question)
            return {
                "answer": answer,
                "retrieved_context": retrieved_docs,
                "mode": "demo",
            }

        rag_context = "\n".join(
            f"- {doc.page_content} (metadata={doc.metadata})" for doc in retrieved_docs
        )

        agent = create_sql_agent(
            llm=self.llm,
            db=self.db,
            agent_type="tool-calling",
            verbose=self.verbose,
            top_k=self.top_k,
            prefix=SYSTEM_PREFIX_TEMPLATE.format(rag_context=rag_context, dialect="{dialect}", top_k="{top_k}"),
        )

        result = agent.invoke({"input": question})
        return {
            "answer": result["output"],
            "retrieved_context": retrieved_docs,
            "mode": "langchain",
        }

    def _answer_in_demo_mode(self, question: str) -> str:
        lower_question = question.lower()
        sql = None
        summary = ""

        if ("tabela" in lower_question or "schema" in lower_question or "esquema" in lower_question) and (
            "banco" in lower_question or "database" in lower_question or "sql" in lower_question
        ):
            return (
                "Resposta em modo de demonstração.\n"
                "As tabelas principais do banco são:\n"
                "- customers: cadastro de clientes, com nome, segmento e cidade.\n"
                "- products: catálogo de produtos e serviços.\n"
                "- orders: pedidos, com data, status e valor total.\n"
                "- order_items: itens de cada pedido, com quantidade e receita por linha.\n\n"
                "Se quiser, você pode perguntar também:\n"
                "- Qual a receita por segmento de cliente?\n"
                "- Quais produtos geraram mais receita?\n"
                "- Quantos pedidos pendentes existem?\n"
                "- Quais são os pedidos pagos mais recentes?\n\n"
                "Defina OPENAI_API_KEY no arquivo .env para habilitar o fluxo completo com LangChain."
            )

        if ("receita" in lower_question or "faturamento" in lower_question or "revenue" in lower_question) and (
            "segment" in lower_question or "segmento" in lower_question
        ):
            sql = """
                SELECT c.segment, ROUND(SUM(o.total_amount), 2) AS revenue
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                WHERE o.status = 'paid'
                GROUP BY c.segment
                ORDER BY revenue DESC
            """
            summary = "Receita de pedidos pagos por segmento de cliente:"
        elif ("pendente" in lower_question or "pending" in lower_question) and (
            "pedido" in lower_question or "order" in lower_question
        ):
            sql = """
                SELECT COUNT(*) AS pending_orders
                FROM orders
                WHERE status = 'pending'
            """
            summary = "Quantidade de pedidos pendentes:"
        elif ("produto" in lower_question or "product" in lower_question) and (
            "receita" in lower_question
            or "faturamento" in lower_question
            or "revenue" in lower_question
            or "top" in lower_question
            or "mais vendidos" in lower_question
        ):
            sql = """
                SELECT p.name, ROUND(SUM(oi.line_total), 2) AS revenue
                FROM order_items oi
                JOIN products p ON p.id = oi.product_id
                JOIN orders o ON o.id = oi.order_id
                WHERE o.status != 'cancelled'
                GROUP BY p.name
                ORDER BY revenue DESC
                LIMIT 5
            """
            summary = "Produtos com maior receita:"
        elif ("recente" in lower_question or "recent" in lower_question or "ultimos" in lower_question) and (
            "pedido" in lower_question or "order" in lower_question
        ):
            sql = """
                SELECT o.id, c.name, o.order_date, o.total_amount
                FROM orders o
                JOIN customers c ON c.id = o.customer_id
                WHERE o.status = 'paid'
                ORDER BY o.order_date DESC
                LIMIT 5
            """
            summary = "Pedidos pagos mais recentes:"
        else:
            return (
                "O app está rodando em modo de demonstração porque a OPENAI_API_KEY não está configurada. "
                "Tente perguntas sobre receita por segmento, pedidos pendentes, produtos com maior receita ou pedidos recentes."
            )

        rows = self._run_sql(sql)
        formatted_rows = "\n".join(str(row) for row in rows)
        return (
            "Resposta em modo de demonstração.\n"
            f"{summary}\n{formatted_rows}\n\n"
            "Defina OPENAI_API_KEY no arquivo .env para habilitar o fluxo completo com LangChain."
        )

    @staticmethod
    def _run_sql(sql: str):
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        connection.close()
        return rows
