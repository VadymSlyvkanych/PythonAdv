from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))

    products: Mapped[list["Product"]] = relationship(back_populates="category", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Category(id={self.id!r}, name={self.name!r}, description={self.description!r})"


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    in_stock: Mapped[bool] = mapped_column(Boolean)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))

    category: Mapped["Category"] = relationship(back_populates="products")

    def __repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, price={self.price!r}, in_stock={self.in_stock!r}, category_id={self.category_id!r})"


def main() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        electronics = Category(name="Electronics", description="Electronic devices and gadgets")
        food = Category(name="Food", description="Various food products")

        session.add_all([electronics, food])
        session.commit()

        laptop = Product(name="Laptop", price=Decimal("999.99"), in_stock=True, category_id=electronics.id)
        smartphone = Product(name="Smartphone", price=Decimal("699.50"), in_stock=False, category_id=electronics.id)
        chocolate = Product(name="Chocolate", price=Decimal("4.99"), in_stock=True, category_id=food.id)

        session.add_all([laptop, smartphone, chocolate])
        session.commit()

        print("=== ALL PRODUCTS ===")
        for product in session.query(Product).all():
            print(f"{product.name} - ${product.price} (In stock: {product.in_stock})")

        print("\n=== PRODUCTS IN STOCK ===")
        for product in session.query(Product).filter(Product.in_stock == True).all():
            print(f"{product.name} - ${product.price}")

        print("\n=== CATEGORIES WITH PRODUCTS ===")
        for category in session.query(Category).all():
            print(f"\n{category.name}:")
            for product in category.products:
                print(f"  - {product.name}")


if __name__ == "__main__":
    from sqlalchemy import create_engine

    main()