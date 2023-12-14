import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from flask_restful import Api
from flask_admin import Admin, AdminIndexView

from .config import config

app = Flask(__name__)
api = Api(app)

ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') + '/my_app/static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'{config["DB_DRIVER"]}://{config["DB_USER"]}:{config["DB_PASSWORD"]}@'
    f'{config["DB_HOST"]}:{config["DB_PORT"]}/{config["DB_NAME"]}'
)
app.secret_key = config['SECRET_KEY']
app.config['WTF_CSRF_SECRET_KEY'] = app.secret_key
app.config["FACEBOOK_OAUTH_CLIENT_ID"] = config['FACEBOOK_ID']
app.config["FACEBOOK_OAUTH_CLIENT_SECRET"] = config['FACEBOOK_SECRET']

app.config["GOOGLE_OAUTH_CLIENT_ID"] = config['GOOGLE_CLIENT_ID']
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = config['GOOGLE_CLIENT_SECRET']
app.config["OAUTHLIB_RELAX_TOKEN_SCOPE"] = True
app.config['LOG_FILE'] = 'application.log'

if not app.debug:
    import logging
    from logging import FileHandler, Formatter
    file_handler = FileHandler(app.config['LOG_FILE'])
    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        )
    )
db = SQLAlchemy(app)

migrate = Migrate(app, db)
CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


from my_app.admin_mod import admin_models


class MyCustom404(Exception):
    pass


from my_app.catalog.views import catalog
app.register_blueprint(catalog)

from my_app.auth.views import auth_route
app.register_blueprint(auth_route)

from my_app.auth.views import facebook_blueprint, google_blueprint
app.register_blueprint(facebook_blueprint)
app.register_blueprint(google_blueprint)

from my_app.api_routes.views import ProductApi
api.add_resource(
    ProductApi,
    '/api/products',
    '/api/products/<int:page>',
    '/api/product/<int:id>'
)

# from my_app.auth.views import HelloView
# admin_mod.add_view(HelloView(name='Hello'))
# from my_app.auth.views import HelloView

with app.app_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(e)
    return render_template('404.html'), 404


@app.errorhandler(MyCustom404)
def special_page_not_found(error):
    app.logger.error(error)
    return render_template("custom_404.html"), 404
