import json
import os
from functools import wraps

import requests
from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for, abort, current_app
# from flask_mail import Message
from sqlalchemy.orm import join
from werkzeug.utils import secure_filename
import boto3
import openai

from my_app import app, db, MyCustom404
from my_app.catalog.models import Product, Category
from .forms import ProductForm, CategoryForm, ProductGPTForm
from my_app import mail
from my_app.tasks import send_mail

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
        return decorated_fn
    return decorated


@catalog.route('/')
@catalog.route('/home')
@template_to_json('home.html')
def home():
    products = Product.query.all()
    current_app.logger.info(f'Home page with total of {len(products)} products')
    return {"count": len(products)}


@catalog.route('/product/<prod_id>')
def product(prod_id):
    product = Product.query.filter_by(id=prod_id).first()
    if not product:
        current_app.logger.warning('Requested product not found')
        abort(404)
    return render_template('product.html', product=product)


@catalog.route('/products')
@catalog.route('/products/<int:page>')
def products(page=1):
    products = Product.query.paginate(page=page, per_page=10)
    return render_template('products.html', products=products)


@catalog.route('/product-create', methods=["GET", "POST",])
def create_product():
    form = ProductForm()
    if form.validate_on_submit():
        name = request.form.get('name')
        price = request.form.get('price')
        categ = Category.query.get_or_404(request.form.get('category'))
        image = form.image.data
        filename = secure_filename(image.filename)
        # image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #  saving image to s3 bucket
        session = boto3.Session(
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        )
        s3 = session.resource('s3')
        bucket = s3.Bucket(current_app.config['AWS_BUCKET'])
        if bucket not in list(s3.buckets.all()):
            bucket = s3.create_bucket(
                Bucket = current_app.config['AWS_BUCKET'],
                CreateBucketConfiguration = {
                    'LocationConstraint':
                        'ap-south-1'},
            )
        bucket.upload_fileobj(
            image,
            filename,
            ExtraArgs={'ACL': 'public-read'}
        )
        new_prod = Product(name=name, price=price, category=categ, image_path=filename)
        db.session.add(new_prod)
        db.session.commit()
        flash('The product %s has been created' % name,'success')
        # if request.headers['Content-Type'] == 'application/multipart/form-data':
        return redirect(url_for('catalog.product', prod_id=new_prod.id))
        # return 'Product created.'
    if form.errors:
        flash(form.errors, 'danger')
    return render_template('product-create.html', form=form)


@catalog.route('/category-create', methods=['GET', 'POST',])
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        name = request.form.get('name')
        category = Category(name)
        db.session.add(category)
        db.session.commit()
        # return 'Category created.'
        flash('The category %s has been created' % name,'success')
        # message = Message("New category added",
        #                   recipients=[app.config['RECEIVER_EMAIL']])
        # message.body = render_template("category-create-email-text.html", category=category)
        # message.html = render_template("category-create-email-html.html", category=category)
        # mail.send(message)
        send_mail.apply_async(args=[category.id, category.name])
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


@catalog.route('/product-search-gpt', methods=['GET', 'POST'])
def product_search_gpt():
    if request.method == 'POST':
        query = request.form.get('query')
        openai.api_key = app.config['OPENAI_KEY']
        prompt = """Context: Ecommerce electronics website\n
        Operation: Create search queries for a product\n
        Product: """ + query
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.2,
            max_tokens=60,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0
        )
        return response['choices'][0]['text'].strip('\n').split('\n')[1:]
    return render_template('product-search-gpt.html')


@catalog.route('/chat-gpt', methods=['GET', 'POST'])
def chat_gpt():
    if request.method == 'POST':
        msg = request.form.get('msg')

        openai.api_key = app.config['OPENAI_KEY']
        messages = [
            {
                "role": "system",
                "content": "You are a helpful chat assistant for a generic electronics Ecommerce website"
            },
            {"role": "user", "content": msg}
        ]

        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages
        )
        return jsonify(
            message=response['choices'][0]['message']['content']
        )
    return render_template('chatgpt.html')


@catalog.route('/product-create-gpt',methods=['GET','POST'])
def create_product_gpt():
    form = ProductGPTForm()
    if form.validate_on_submit():
        name = request.form.get('name')
        price = request.form.get('price')
        category = Category.query.get_or_404(request.form.get('category'))

        openai.api_key = app.config['OPENAI_KEY']

        prompt = "Generate an image for a " + name + " on a white background for a classy e - commerce store listing"
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="512x512"
        )
        image_url = response['data'][0]['url']
        filename = secure_filename(name + '.png')
        response = requests.get(image_url)

        # session = boto3.Session(
        #     aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
        #     aws_secret_access_key=current_app.config['AWS_SECRET_KEY']
        # )
        # s3 = session.resource('s3')
        # bucket = s3.Bucket(current_app.config['AWS_BUCKET'])
        # if bucket not in list(s3.buckets.all()):
        #     bucket = s3.create_bucket(
        #         Bucket=current_app.config['AWS_BUCKET'],
        #         CreateBucketConfiguration={
        #             'LocationConstraint':
        #                 'ap-south-1'},
        #     )
        # bucket.upload_fileobj(
        #     response.content,
        #     filename,
        #     ExtraArgs={'ACL': 'public-read'}
        # )

        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "wb") as file:
            file.write(response.content)
        product = Product(name, price, category, filename)
        db.session.add(product)
        db.session.commit()

        flash(f'The product {name} has been created', 'success')
        return redirect(url_for('catalog.product', prod_id=product.id))
    if form.errors:
        flash(form.errors, 'danger')

    return render_template('product-create-gpt.html', form=form)
