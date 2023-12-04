from flask import Flask
from my_app.products.views import products_blueprint

app = Flask(__name__)
app.register_blueprint(products_blueprint)
