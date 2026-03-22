from pathlib import Path

from sqlalchemy import Column, Float, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from .config import DB_PATH


Base = declarative_base()


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    segment = Column(String, nullable=False)
    city = Column(String, nullable=False)

    orders = relationship("Order", back_populates="customer")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)

    items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(String, nullable=False)
    status = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)

    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    line_total = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="items")


CUSTOMERS = [
    {"id": 1, "name": "Ana Souza", "segment": "Enterprise", "city": "Sao Paulo"},
    {"id": 2, "name": "Carlos Lima", "segment": "SMB", "city": "Rio de Janeiro"},
    {"id": 3, "name": "Juliana Alves", "segment": "Enterprise", "city": "Belo Horizonte"},
    {"id": 4, "name": "Marcos Silva", "segment": "Startup", "city": "Curitiba"},
    {"id": 5, "name": "Fernanda Rocha", "segment": "SMB", "city": "Recife"},
]

PRODUCTS = [
    {"id": 1, "name": "Analytics Cloud", "category": "Software", "unit_price": 1200.0},
    {"id": 2, "name": "SQL Copilot", "category": "Software", "unit_price": 850.0},
    {"id": 3, "name": "Onboarding Package", "category": "Services", "unit_price": 400.0},
    {"id": 4, "name": "Premium Support", "category": "Services", "unit_price": 650.0},
    {"id": 5, "name": "Data Integration API", "category": "Platform", "unit_price": 980.0},
]

ORDERS = [
    {"id": 101, "customer_id": 1, "order_date": "2025-01-15", "status": "paid", "total_amount": 2050.0},
    {"id": 102, "customer_id": 2, "order_date": "2025-01-20", "status": "paid", "total_amount": 1250.0},
    {"id": 103, "customer_id": 3, "order_date": "2025-02-03", "status": "pending", "total_amount": 2180.0},
    {"id": 104, "customer_id": 4, "order_date": "2025-02-18", "status": "paid", "total_amount": 850.0},
    {"id": 105, "customer_id": 5, "order_date": "2025-03-01", "status": "cancelled", "total_amount": 400.0},
    {"id": 106, "customer_id": 1, "order_date": "2025-03-10", "status": "paid", "total_amount": 1630.0},
    {"id": 107, "customer_id": 3, "order_date": "2025-03-12", "status": "paid", "total_amount": 1850.0},
    {"id": 108, "customer_id": 2, "order_date": "2025-03-21", "status": "pending", "total_amount": 980.0},
]

ORDER_ITEMS = [
    {"id": 1001, "order_id": 101, "product_id": 1, "quantity": 1, "line_total": 1200.0},
    {"id": 1002, "order_id": 101, "product_id": 4, "quantity": 1, "line_total": 650.0},
    {"id": 1003, "order_id": 101, "product_id": 3, "quantity": 1, "line_total": 200.0},
    {"id": 1004, "order_id": 102, "product_id": 2, "quantity": 1, "line_total": 850.0},
    {"id": 1005, "order_id": 102, "product_id": 3, "quantity": 1, "line_total": 400.0},
    {"id": 1006, "order_id": 103, "product_id": 1, "quantity": 1, "line_total": 1200.0},
    {"id": 1007, "order_id": 103, "product_id": 5, "quantity": 1, "line_total": 980.0},
    {"id": 1008, "order_id": 104, "product_id": 2, "quantity": 1, "line_total": 850.0},
    {"id": 1009, "order_id": 105, "product_id": 3, "quantity": 1, "line_total": 400.0},
    {"id": 1010, "order_id": 106, "product_id": 5, "quantity": 1, "line_total": 980.0},
    {"id": 1011, "order_id": 106, "product_id": 4, "quantity": 1, "line_total": 650.0},
    {"id": 1012, "order_id": 107, "product_id": 1, "quantity": 1, "line_total": 1200.0},
    {"id": 1013, "order_id": 107, "product_id": 4, "quantity": 1, "line_total": 650.0},
    {"id": 1014, "order_id": 108, "product_id": 5, "quantity": 1, "line_total": 980.0},
]


def create_sample_database(db_path: Path | None = None, reset: bool = False) -> Path:
    db_path = db_path or DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{db_path}")
    if reset:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    for row in CUSTOMERS:
        session.merge(Customer(**row))
    for row in PRODUCTS:
        session.merge(Product(**row))
    for row in ORDERS:
        session.merge(Order(**row))
    for row in ORDER_ITEMS:
        session.merge(OrderItem(**row))
    session.commit()
    session.close()
    engine.dispose()

    return db_path


def ensure_sample_database(db_path: Path | None = None) -> Path:
    db_path = db_path or DB_PATH
    if db_path.exists():
        return db_path
    return create_sample_database(db_path, reset=False)


if __name__ == "__main__":
    path = create_sample_database(reset=True)
    print(f"Sample database created at: {path}")
