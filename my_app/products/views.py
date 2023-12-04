from werkzeug.exceptions import abort
from flask import Blueprint, render_template
from my_app.products.models import PRODUCTS

products_blueprint = Blueprint('product', __name__)


@products_blueprint.route('/')
@products_blueprint.route('/home')
def home():
    return render_template('home.html', products=PRODUCTS)


@products_blueprint.route('/product/<key>')
def get_product(key):
    product = PRODUCTS.get(key)
    if not product:
        abort(404)
    return render_template('product.html', product=product)


@products_blueprint.context_processor
def custom_processor():
    def full_name(product):
        return '{0} / {1}'.format(product['category'], product['name'])
    return {'full_name': full_name}


@products_blueprint.app_template_filter('full_name')
def full_name_filter(product):
    return '{0} | {1}'.format(product['category'], product['name'])