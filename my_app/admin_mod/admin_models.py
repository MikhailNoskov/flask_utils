from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_admin.form import rules
from wtforms import PasswordField

from my_app import db, app
from my_app.auth.models import User
from my_app.catalog.models import Product, Category


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


class UserAdminView(ModelView):
    column_searchable_list = ('username',)
    column_sortable_list = ('username', 'admin')
    column_exclude_list = ('pwdhash',)
    form_excluded_columns = ('pwdhash',)
    form_edit_rules = ('username', 'admin')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password = PasswordField('Password')
        return form_class

    def create_model(self, form):
        model = self.model(form.username.data, form.password.data, form.admin.data)
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()


class ProductAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


class CategoryAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(UserAdminView(User, db.session))
admin.add_view(ProductAdminView(Product, db.session))
admin.add_view(CategoryAdminView(Category, db.session))
