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
    def create_product(cls, name, price, category, image=None):
        category = Category.query.filter_by(name=category).first()
        if not category:
            category = Category(category)
        product = Product(name=name, price=price, category=category, image_path=image)
        db.session.add(product)
        db.session.commit()
        return product

    @classmethod
    def update_product(cls, id, name, price, category):
        category = Category.query.filter_by(name=category).first()
        if not category:
            category = Category(category)
        Product.query.filter_by(id=id).update({
            'name': name,
            'price': price,
            'category_id': category.id,
        })
        db.session.commit()
        return cls.get_product(id=id)
