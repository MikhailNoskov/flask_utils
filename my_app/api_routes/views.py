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
        return self.service.put(id=id)

    def delete(self, id):
        product = Product.query.filter_by(id=id)
        product.delete()
        db.session.commit()
        return json.dumps({'response': 'Success'})
