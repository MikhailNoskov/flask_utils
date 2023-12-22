from my_app import app, db, MyCustom404
from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for, abort, current_app

from my_app.catalog.models import Product


class ProductTemplateService:

    @classmethod
    def get_products(cls, page):
        products = Product.query.paginate(page=page, per_page=10)
        return render_template('products.html', products=products)

    @classmethod
    def get_product(cls, id):
        product = Product.query.filter_by(id=id).first()
        if not product:
            current_app.logger.warning('Requested product not found')
            abort(404)
        return render_template('product.html', product=product)

    def create_product(self):
        pass
