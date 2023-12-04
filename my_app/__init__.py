from flask import Flask, request
from my_app.products.views import products_blueprint
import ccy

app = Flask(__name__)
app.register_blueprint(products_blueprint)


@app.template_filter('format_currency')
def format_currency_filter(amount):
    currency_code = ccy.countryccy(request.accept_languages.best[-2:])
    return '{0} {1}'.format(currency_code, amount)
