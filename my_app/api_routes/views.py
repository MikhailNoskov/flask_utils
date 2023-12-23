import json

from flask import abort, request
from flask_restful import Resource, reqparse

from my_app.catalog.models import Product, Category
from my_app import db
from .services import ProductAPIService

parser = reqparse.RequestParser()
parser.add_argument('name', type=str)
parser.add_argument('price', type=float)
parser.add_argument('category', type=dict)


class ProductApi(Resource):
    service = ProductAPIService

    def get(self, id=None, page=1):
        return self.service.get(id=id, page=page)

    def post(self):
        return self.service.post()

    def put(self, id):
        args = parser.parse_args()
        name = args['name']
        price = args['price']
        categ_name = args['category']['name']
        category = Category.query.filter_by(name=categ_name).first()
        Product.query.filter_by(id=id).update({
            'name': name,
            'price': price,
            'category_id': category.id,
        })
        db.session.commit()
        product = Product.query.get_or_404(id)
        res = {}
        res[product.id] = {
            'name': product.name,
            'price': product.price,
            'category': product.category.name,
        }
        return json.dumps(res)

    def delete(self, id):
        product = Product.query.filter_by(id=id)
        product.delete()
        db.session.commit()
        return json.dumps({'response': 'Success'})
