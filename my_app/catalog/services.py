import tempfile

from my_app import app, db, MyCustom404
from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for, abort, current_app
from werkzeug.utils import secure_filename
import boto3

from my_app.catalog.models import Product, Category
from .forms import ProductForm, CategoryForm, ProductGPTForm
from my_app.db_services.product_db_services import ProductDBService
from my_app.tasks import save_image_async


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
            name = form.name.data
            price = form.price.data
            categ = form.category.name
            image = form.image.data
            if image:
                temp_image = tempfile.NamedTemporaryFile(delete=False)
                image.save(temp_image.name)
                image_path = temp_image.name
                filename = secure_filename(image.filename)
                save_image_async.apply_async(args=[image_path, filename])
                new_prod = cls.db_service.create_product(name=name, price=price, category=categ, image=filename)
                flash('The product %s has been created' % name, 'success')
                return redirect(url_for('catalog.product', prod_id=new_prod.id))
            new_prod = cls.db_service.create_product(name=name, price=price, category=categ)
            flash('The product %s has been created' % name, 'success')
            return redirect(url_for('catalog.product', prod_id=new_prod.id))
        if form.errors:
            flash(form.errors, 'danger')
        return render_template('product-create.html', form=form)
