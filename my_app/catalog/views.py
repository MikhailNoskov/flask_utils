from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for
from sqlalchemy.orm import join

from functools import wraps

from my_app import db, MyCustom404
from my_app.catalog.models import Product, Category
from .forms import ProductForm, CategoryForm

catalog = Blueprint('catalog', __name__)


def template_to_json(template=None):
    """Return a dict from your view and this will either pass it to a template or render json. Use like:
    @template_or_json('template.html')
    """
    def decorated(func):
        @wraps(func)
        def decorated_fn(*args, **kwargs):
            ctx = func(*args, **kwargs)
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or not template:
                return jsonify(ctx)
            else:
                return render_template(template, **ctx)
        return  decorated_fn
    return decorated


@catalog.route('/')
@catalog.route('/home')
@template_to_json('home.html')
def home():
    # if request.headers.get("X-Requested-With") == "XMLHttpRequest":
    products = Product.query.all()
    #     return jsonify({'count': len(products)})
    # # return "Welcome to catalog home"
    # return render_template('home.html')
    return {"count": len(products)}


@catalog.route('/product/<prod_id>')
def product(prod_id):
    product = Product.query.get_or_404(prod_id)
    # return 'Product - {}, ${}'.format(prod.name, prod.price)
    return render_template('product.html', product=product)


@catalog.route('/products')
@catalog.route('/products/<int:page>')
def products(page=1):
    # prods = Product.query.all()
    # prods = Product.query.paginate(page=page, per_page=10).items
    products = Product.query.paginate(page=page, per_page=10)
    # response = {}
    # for prod in prods:
    #     response[prod.id] = {
    #         "name": prod.name,
    #         "price": prod.price,
    #         'category': prod.category.name,
    #         'company': prod.company
    #     }
    # print(prods)
    # return jsonify(response)
    return render_template('products.html', products=products)


@catalog.route('/product-create', methods=["GET", "POST",])
def create_product():
    form = ProductForm(meta={'csrf': False})
    if form.validate_on_submit():
        name = request.form.get('name')
        price = request.form.get('price')
        categ = Category.query.get_or_404(request.form.get('category'))
        new_prod = Product(name, price, categ)
        db.session.add(new_prod)
        db.session.commit()
        flash('The product %s has been created' % name,'success')
        if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            return redirect(url_for('catalog.product', prod_id=new_prod.id))
        return 'Product created.'
    if form.errors:
        flash(form.errors, 'danger')
    return render_template('product-create.html', form=form)


@catalog.route('/category-create', methods=['GET', 'POST',])
def create_category():
    form = CategoryForm(meta={'csrf': False})
    if form.validate_on_submit():
        name = request.form.get('name')
        category = Category(name)
        db.session.add(category)
        db.session.commit()
        # return 'Category created.'
        flash('The category %s has been created' % name,'success')
        return render_template('category.html', category=category)
    if form.errors:
        flash(form.errors, 'danger')
    return render_template('category-create.html', form=form)


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
    # return jsonify(res)
    return render_template('categories.html', categories=categories)


@catalog.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    print(category.name)
    return render_template('category.html', category=category)


@catalog.route('/custom_exception')
def exception_404():
    raise MyCustom404


@catalog.route('/product-search')
@catalog.route('/product-search/<int:page>')
def product_search(page=1):
    name = request.args.get('name')
    price = request.args.get('price')
    company = request.args.get('company')
    category = request.args.get('category')
    products = Product.query
    if name:
        products = products.filter(Product.name.like('%' + name + '%'))
    if price:
        products = products.filter(Product.price == price)
    if company:
        products = products.filter(Product.company.like('%' + company + '%'))
    if category:
        products = products.select_from(join(Product, Category)).filter(Category.name.like('%' + category + '%'))
    return render_template('products.html', products=products.paginate(page=page, per_page=10))
