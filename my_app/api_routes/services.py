from my_app import app, db, MyCustom404
from flask import request, jsonify, Blueprint, render_template, flash, redirect, url_for, abort, current_app
from werkzeug.utils import secure_filename
import boto3

from my_app.catalog.models import Product, Category


class ProductAPIService:

    @classmethod
    def get_products(cls, page):
        pass

    @classmethod
    def get_product(cls, id):
        pass

    @classmethod
    def create_product(cls):
        pass
