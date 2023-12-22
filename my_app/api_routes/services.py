import json

from my_app import app, db, MyCustom404
from flask import abort
from flask_restful import Resource, reqparse
from werkzeug.utils import secure_filename
import boto3

from my_app.catalog.models import Product, Category


class ProductAPIService:
    parser = reqparse.RequestParser()

    @classmethod
    def _init_parser(cls):
        cls.parser.add_argument('name', type=str)
        cls.parser.add_argument('price', type=float)
        cls.parser.add_argument('category', type=dict)
        return cls.parser

    @classmethod
    def get(cls, id=None, page=1):
        if not id:
            products = Product.query.paginate(page=page, per_page=10).items
        else:
            products = [Product.query.get(id)]
        if not products:
            abort(404)
        res = {}
        for product in products:
            res[product.id] = {
                'name': product.name,
                'price': product.price,
                'category': product.category.name
            }
        return json.dumps(res)

    @classmethod
    def post(cls):
        args = cls._init_parser().parse_args()
        name = args['name']
        price = args['price']
        categ_name = args['category']['name']
        category = Category.query.filter_by(name=categ_name).first()
        if not category:
            category = Category(categ_name)
        product = Product(name=name, price=price, category=category)
        db.session.add(product)
        db.session.commit()
        res = {}
        res[product.id] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name,
        }
        return json.dumps(res)
