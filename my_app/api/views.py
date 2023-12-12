import os
import json
from functools import wraps

from flask.views import MethodView
from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for, abort
from sqlalchemy.orm import join
from werkzeug.utils import secure_filename

from my_app import app, db, MyCustom404, ALLOWED_EXTENSIONS
from my_app.catalog.models import Product, Category


class ProductView(MethodView):
    def get(self, id=None, page=1):
        if not id:
            products = Product.query.paginate(page=page, per_page=10).items
            res = {}
            for product in products:
                res[product.id] = {
                    'name': product.name,
                    'price': product.price,
                    'category': product.category.name
                }
        else:
            product = Product.query.filter_by(id=id).first()
            if not product:
                abort(404)
            res = json.dumps(
                {
                    'name': product.name,
                    'price': product.price,
                    'category': product.category.name}
            )
        return res

    def post(self):
        pass

    def put(self, id):
        pass

    def delete(self):
        pass
