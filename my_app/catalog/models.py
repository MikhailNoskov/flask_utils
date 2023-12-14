from my_app import db


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'))
    company = db.Column(db.String(100))
    image_path = db.Column(db.String(255))

    def __init__(self, name, price, category, image_path=None):
        self.name = name
        self.price = price
        self.image_path = image_path
        self.category = category

    def __repr__(self):
        return f'<Product {self.id}>'


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Category {self.id}>'
