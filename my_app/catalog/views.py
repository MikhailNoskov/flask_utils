from flask import request, jsonify, Blueprint

from my_app import db
from my_app.catalog.models import Product

catalog = Blueprint('catalog', __name__)


@catalog.route('/')
@catalog.route('/home')
def home():
    return "Welcome to catalog home"


@catalog.route('/product/<prod_id>')
def product(prod_id):
    prod = Product.query.get_or_404(prod_id)
    return 'Product - {}, ${}'.format(prod.name, prod.price)


@catalog.route('/products')
def products():
    prods = Product.query.all()
    response = {}
    for prod in prods:
        response[prod.id] = {
            "name": prod.name,
            "price": prod.price
        }

    return jsonify(response)


@catalog.route('/product-create', methods=["POST",])
def create_product():
    name = request.form.get('name')
    price = request.form.get('price')
    new_prod = Product(name, price)
    db.session.add(new_prod)
    db.session.commit()
    return 'Product created.'
