from my_app import app, db, MyCustom404
from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for, abort, current_app
from werkzeug.utils import secure_filename
import boto3

from my_app.catalog.models import Product, Category
from .forms import ProductForm, CategoryForm, ProductGPTForm
from my_app.db_services.product_db_services import ProductDBService


class ProductTemplateService:
    db_service = ProductDBService

    @classmethod
    def get_products(cls, page):
        products = cls.db_service.get_products(page=page)
        return render_template('products.html', products=products)

    @classmethod
    def get_product(cls, id):
        product = cls.db_service.get_product(id=id)
        if not product:
            current_app.logger.warning('Requested product not found')
            abort(404)
        return render_template('product.html', product=product)

    @classmethod
    def create_product(cls):
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
                    Bucket=current_app.config['AWS_BUCKET'],
                    CreateBucketConfiguration={
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
            flash('The product %s has been created' % name, 'success')
            # if request.headers['Content-Type'] == 'application/multipart/form-data':
            return redirect(url_for('catalog.product', prod_id=new_prod.id))
            # return 'Product created.'
        if form.errors:
            flash(form.errors, 'danger')
        return render_template('product-create.html', form=form)
