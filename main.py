from src.config import is_default_sample_database, load_settings
from src.sample_database import ensure_sample_database
from src.sql_rag_agent import SQLRAGAssistant


def main():
    settings = load_settings()
    if is_default_sample_database(settings["database_uri"]):
        ensure_sample_database()
    assistant = SQLRAGAssistant(top_k=5, verbose=False)

    print("RAG NLP SQL Assistant")
    print("-" * 40)
    print("Type 'exit' to quit.")

    while True:
        question = input("\nAsk a question about the SQL database: ").strip()
        if not question or question.lower() == "exit":
            break

        result = assistant.ask(question)
        print("\nAnswer:")
        print(result["answer"])
        print("\nRetrieved context:")
        for doc in result["retrieved_context"]:
            print(f"- {doc.page_content}")


if __name__ == "__main__":
    main()
