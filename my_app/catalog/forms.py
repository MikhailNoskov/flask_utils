from decimal import Decimal

from wtforms import StringField, DecimalField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired, NumberRange


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    price = DecimalField('Price', validators=[InputRequired(), NumberRange(min=Decimal('0.0'))])
    category = SelectField('Category', coerce=int, validators=[InputRequired()])
