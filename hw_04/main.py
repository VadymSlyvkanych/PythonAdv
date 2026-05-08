from decimal import Decimal
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Numeric, Boolean


class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))

    products: Mapped[list["Product"]] = relationship(back_populates="category")

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
    from sqlalchemy import create_engine

    engine = create_engine("sqlite:///database.db")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Задача 1: Наполнение данными
        print("=== ЗАДАЧА 1: НАПОЛНЕНИЕ ДАННЫМИ ===")

        # Добавление категорий
        electronics = Category(name="Электроника", description="Гаджеты и устройства.")
        books = Category(name="Книги", description="Печатные книги и электронные книги.")
        clothing = Category(name="Одежда", description="Одежда для мужчин и женщин.")

        session.add_all([electronics, books, clothing])
        session.commit()

        # Добавление продуктов
        smartphone = Product(name="Смартфон", price=Decimal("299.99"), in_stock=True, category_id=electronics.id)
        laptop = Product(name="Ноутбук", price=Decimal("499.99"), in_stock=True, category_id=electronics.id)
        novel = Product(name="Научно-фантастический роман", price=Decimal("15.99"), in_stock=True, category_id=books.id)
        jeans = Product(name="Джинсы", price=Decimal("40.50"), in_stock=True, category_id=clothing.id)
        tshirt = Product(name="Футболка", price=Decimal("20.00"), in_stock=True, category_id=clothing.id)

        session.add_all([smartphone, laptop, novel, jeans, tshirt])
        session.commit()

        print("Данные успешно добавлены в базу данных.")

        # Задача 2: Чтение данных
        print("\n=== ЗАДАЧА 2: ЧТЕНИЕ ДАННЫХ ===")

        categories_with_products = session.query(Category).all()
        for category in categories_with_products:
            print(f"\nКатегория: {category.name} - {category.description}")
            for product in category.products:
                print(f"  - {product.name}: {product.price}")

        # Задача 3: Обновление данных
        print("\n=== ЗАДАЧА 3: ОБНОВЛЕНИЕ ДАННЫХ ===")

        smartphone_to_update = session.query(Product).filter(Product.name == "Смартфон").first()
        if smartphone_to_update:
            smartphone_to_update.price = Decimal("349.99")
            session.commit()
            print(f"Цена смартфона обновлена на {smartphone_to_update.price}")
        else:
            print("Смартфон не найден")

        # Задача 4: Агрегация и группировка
        print("\n=== ЗАДАЧА 4: АГРЕГАЦИЯ И ГРУППИРОВКА ===")

        category_counts = session.query(
            Category.name,
            func.count(Product.id).label('product_count')
        ).join(
            Product, Category.id == Product.category_id
        ).group_by(Category.name).all()

        for category_name, count in category_counts:
            print(f"Категория '{category_name}': {count} продуктов")

        # Задача 5: Группировка с фильтрацией
        print("\n=== ЗАДАЧА 5: ГРУППИРОВКА С ФИЛЬТРАЦИЕЙ ===")

        categories_with_multiple_products = session.query(
            Category.name,
            func.count(Product.id).label('product_count')
        ).join(
            Product, Category.id == Product.category_id
        ).group_by(Category.name).having(
            func.count(Product.id) > 1
        ).all()

        print("Категории с более чем одним продуктом:")
        for category_name, count in categories_with_multiple_products:
            print(f"  - {category_name}: {count} продуктов")


if __name__ == "__main__":
    main()