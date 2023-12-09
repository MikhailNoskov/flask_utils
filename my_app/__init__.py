import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

from .config import config

app = Flask(__name__)
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') + '/my_app/static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'{config["DB_DRIVER"]}://{config["DB_USER"]}:{config["DB_PASSWORD"]}@'
    f'{config["DB_HOST"]}:{config["DB_PORT"]}/{config["DB_NAME"]}'
)
app.secret_key = config['SECRET_KEY']
app.config['WTF_CSRF_SECRET_KEY'] = app.secret_key
db = SQLAlchemy(app)
migrate = Migrate(app, db)
CSRFProtect(app)


class MyCustom404(Exception):
    pass


from my_app.catalog.views import catalog
app.register_blueprint(catalog)

with app.app_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(MyCustom404)
def special_page_not_found(error):
    return render_template("custom_404.html"), 404
