from wtforms import StringField, DecimalField, SelectField
from flask_wtf import FlaskForm


class ProductForm(FlaskForm):
    name = StringField('Name')
    price = DecimalField('Price')
    category = SelectField('Category', coerce=int)
