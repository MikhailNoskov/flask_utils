import json

from flask import abort
from flask_restful import reqparse

from my_app.db_services.product_db_services import ProductDBService


class ProductAPIService:
    parser = reqparse.RequestParser()
    db_service = ProductDBService

    @classmethod
    def _init_parser(cls):
        cls.parser.add_argument('name', type=str)
        cls.parser.add_argument('price', type=float)
        cls.parser.add_argument('category', type=dict)
        return cls.parser

    @classmethod
    def get(cls, id=None, page=1):
        res = dict()
        if not id:
            products = cls.db_service.get_products(page=page)
        else:
            products = [cls.db_service.get_product(id=id)]
        if not products or None in products:
            abort(404)

        for product in products:
            res[product.id] = {
                'name': product.name,
                'price': product.price,
                'category': product.category.name
            }
        return json.dumps(res)

    @classmethod
    def post(cls):
        res = dict()
        args = cls._init_parser().parse_args()
        name = args['name']
        price = args['price']
        category = args['category']['name']
        product = cls.db_service.create_product(name=name, price=price, category=category)
        res[product.id] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name,
        }
        return json.dumps(res)

    @classmethod
    def put(cls, id):
        args = cls._init_parser().parse_args()
        name = args['name']
        price = args['price']
        categ_name = args['category']['name']
        product = cls.db_service.update_product(id=id, name=name, price=price, category=categ_name)
        res = dict()
        res[product.id] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name,
        }
        return json.dumps(res)

    @classmethod
    def delete(cls, id):
        cls.db_service.delete_product(id=id)
        return json.dumps({'response': 'Success'})
