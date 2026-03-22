from langchain_core.documents import Document


def build_context_documents():
    return [
        Document(
            page_content=(
                "customers stores customer master data. "
                "segment can be Enterprise, SMB, or Startup. "
                "city stores the customer's main city."
            ),
            metadata={"source": "data_dictionary", "table": "customers"},
        ),
        Document(
            page_content=(
                "orders stores one row per transaction. "
                "status can be paid, pending, or cancelled. "
                "total_amount is the order header total."
            ),
            metadata={"source": "data_dictionary", "table": "orders"},
        ),
        Document(
            page_content=(
                "order_items stores the line-level details for each order. "
                "Use it when the user asks about product mix, quantities, or revenue by product."
            ),
            metadata={"source": "data_dictionary", "table": "order_items"},
        ),
        Document(
            page_content=(
                "products stores product catalog information. "
                "category groups products into Software, Services, and Platform."
            ),
            metadata={"source": "data_dictionary", "table": "products"},
        ),
        Document(
            page_content=(
                "To calculate revenue by segment, join customers to orders on customer_id and filter out cancelled orders when needed."
            ),
            metadata={"source": "query_hint", "topic": "segment_revenue"},
        ),
        Document(
            page_content=(
                "To identify top-selling products, join products, order_items, and orders. "
                "Use SUM(order_items.line_total) for revenue and SUM(order_items.quantity) for units."
            ),
            metadata={"source": "query_hint", "topic": "product_sales"},
        ),
        Document(
            page_content=(
                "When the user asks for recent activity, use order_date and sort descending. "
                "Dates are stored as text in ISO format YYYY-MM-DD."
            ),
            metadata={"source": "query_hint", "topic": "dates"},
        ),
    ]
