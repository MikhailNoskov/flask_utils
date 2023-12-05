from my_app import db


class Product(db.Model):
    id = db.Column(db.Integer, primery_key=True)
    name = db.Column(db.String(255))
    price = db.Column(db.Float)

    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __repr__(self):
        return f'<Product {self.id}>'
