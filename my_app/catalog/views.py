from flask import request, jsonify, Blueprint

from my_app import db
from my_app.catalog.models import Product, Category

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
@catalog.route('/products/<int:page>')
def products(page=1):
    # prods = Product.query.all()
    prods = Product.query.paginate(page=page, per_page=10).items
    response = {}
    for prod in prods:
        response[prod.id] = {
            "name": prod.name,
            "price": prod.price,
            'category': prod.category.name,
            'company': prod.company
        }

    return jsonify(response)


@catalog.route('/product-create', methods=["POST",])
def create_product():
    name = request.form.get('name')
    price = request.form.get('price')
    categ_name = request.form.get('category')
    category = Category.query.filter_by(name=categ_name).first()
    if not category:
        category = Category(categ_name)
    new_prod = Product(name, price, category)
    db.session.add(new_prod)
    db.session.commit()
    return 'Product created.'


@catalog.route('/category-create', methods=['POST',])
def create_category():
    name = request.form.get('name')
    category = Category(name)
    db.session.add(category)
    db.session.commit()
    return 'Category created.'


@catalog.route('/categories')
def categories():
    categories = Category.query.all()
    res = {}
    for category in categories:
        res[category.id] = {
            'name': category.name
        }
        for prod in category.products:
            res[category.id]['products'] = {
                'id': prod.id,
                'name': prod.name,
                'price': prod.price
            }
    return jsonify(res)
