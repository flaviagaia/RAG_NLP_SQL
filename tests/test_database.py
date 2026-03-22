import sqlite3
import tempfile
import unittest
from pathlib import Path

from src.config import DB_PATH
from src.sample_database import create_sample_database
from src.sql_rag_agent import SQLRAGAssistant


class SampleDatabaseTest(unittest.TestCase):
    def test_database_creation_and_seed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "sample.db"
            create_sample_database(db_path)

            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            customer_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM orders")
            order_count = cursor.fetchone()[0]
            connection.close()

            self.assertEqual(customer_count, 5)
            self.assertEqual(order_count, 8)

    def test_demo_mode_answer_without_openai_key(self):
        if not DB_PATH.exists():
            create_sample_database()
        assistant = SQLRAGAssistant(top_k=5, verbose=False)
        result = assistant.ask("What is the total paid revenue by customer segment?")

        self.assertIn("Resposta em modo de demonstração", result["answer"])
        self.assertEqual(result["mode"], "demo")


if __name__ == "__main__":
    unittest.main()
