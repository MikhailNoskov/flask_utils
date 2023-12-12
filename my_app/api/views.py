import os
import json
from functools import wraps

from flask import request, jsonify, Blueprint, MethodView, render_template, flash, redirect, url_for
from sqlalchemy.orm import join
from werkzeug.utils import secure_filename

from my_app import app, db, MyCustom404, ALLOWED_EXTENSIONS
from my_app.catalog.models import Product, Category

api_route = Blueprint('api', __name__)
