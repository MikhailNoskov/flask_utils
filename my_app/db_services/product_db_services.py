from my_app import app, db, MyCustom404
from my_app.catalog.models import Product, Category


class ProductDBService:

    @classmethod
    def get_products(cls, page=1):
        return Product.query.paginate(page=page, per_page=10)

    @classmethod
    def get_product(cls, id):
        return Product.query.filter_by(id=id).first()

    @classmethod
    def create_product(cls, name, price, category):
        category = Category.query.filter_by(name=category).first()
        if not category:
            category = Category(category)
        product = Product(name=name, price=price, category=category)
        db.session.add(product)
        db.session.commit()
        return product
