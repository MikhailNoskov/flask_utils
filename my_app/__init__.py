from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'{config["DB_DRIVER"]}://{config["DB_USER"]}:{config["DB_PASSWORD"]}@'
    f'{config["DB_HOST"]}:{config["DB_PORT"]}/{config["DB_NAME"]}'
)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from my_app.catalog.views import catalog
app.register_blueprint(catalog)

with app.app_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
