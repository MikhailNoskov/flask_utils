from decimal import Decimal
from flask import request, jsonify, Blueprint

from my_app.catalog.models import Product

catalog = Blueprint('catalog', __name__)


@catalog.route('/')
@catalog.route('/home')
def home():
    return "Welcome to catalog home"


@catalog.route('/product/<key>')
def product(key):
    prod = Product.objects.get_or_404(key=key)
    return 'Product - {}, ${}'.format(prod.name, prod.price)


@catalog.route('/products')
def products():
    prods = Product.objects.all()
    response = {}
    for prod in prods:
        response[prod.id] = {
            "name": prod.name,
            "price": prod.price,
        }
    return jsonify(response)


@catalog.route('/product-create', methods=["POST",])
def create_product():
    name = request.form.get('name')
    key = request.form.get('key')
    price = request.form.get('price')
    new_prod = Product(name=name, key=key, price=Decimal(price))
    new_prod.save()
    return 'Product created.'
