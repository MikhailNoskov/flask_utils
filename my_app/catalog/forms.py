from decimal import Decimal

import flask
from markupsafe import Markup
from wtforms import StringField, DecimalField, SelectField
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import InputRequired, NumberRange, ValidationError
from wtforms.widgets import Select, html_params

from .models import Category


def check_duplicate_category(case_sensitive=True):
    def _check_duplicate(form, field):
        if case_sensitive:
            res = Category.query.filter(Category.name.like('%' + field.data + '%')).first()

        else:
            res = Category.query.filter(Category.name.ilike('%' + field.data + '%')).first()
        if res:
            raise ValidationError('Category named %s already exists' % field.data)
    return _check_duplicate


class CustomCategoryInput(Select):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        for val, label, selected in field.iter_choices():
            html.append(
                '<input type="radio" %s> %s' % (html_params(
                    name=field.name, value=val, checked=selected, ** kwargs
                    ), label
            )
            )
        return Markup(' '.join(html))


class CategoryField(SelectField):
    # widget = CustomCategoryInput()

    def iter_choices(self):
        categories = [("", "")] + [(c.id, c.name) for c in Category.query.all()]
        for value, label in categories:
            if value == label == '':
                yield value, label, True
            else:
                yield value, label, self.coerce(value) == self.data

    def pre_validate(self, form):
        for v, _ in [(c.id, c.name) for c in Category.query.all()]:
            if self.data == v:
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))


class BasicForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])


class ProductForm(BasicForm):
    price = DecimalField('Price', validators=[InputRequired(), NumberRange(min=Decimal('0.0'))])
    category = CategoryField('Category', coerce=int, validators=[InputRequired()])
    image = FileField('Product Image')


class CategoryForm(BasicForm):
    name = StringField('Name', validators=[InputRequired(), check_duplicate_category()])


class ProductGPTForm(BasicForm):
    price = DecimalField('Price', validators=[InputRequired(), NumberRange(min=Decimal('0.0'))])
    category = CategoryField('Category', coerce=int, validators=[InputRequired()])
