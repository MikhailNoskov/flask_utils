from flask import flash
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_admin.form import rules
from flask_admin.actions import ActionsMixin
from werkzeug.security import generate_password_hash
from wtforms import PasswordField

from my_app import db, app
from my_app.auth.models import User
from my_app.catalog.models import Product, Category


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()


class UserAdminView(ModelView, ActionsMixin):
    column_searchable_list = ('username',)
    column_sortable_list = ('username', 'admin')
    column_exclude_list = ('pwdhash',)
    form_excluded_columns = ('pwdhash',)
    # form_edit_rules = ('username', 'admin')
    form_edit_rules = ('username', 'admin', 'roles', rules.Header('Reset Password'),)
    form_create_rules = ('username', 'admin', 'roles', 'password')

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def scaffold_form(self):
        form_class = super(UserAdminView, self).scaffold_form()
        form_class.password = PasswordField('Password')
        return form_class

    def create_model(self, form):
        if 'C' not in current_user.roles:
            flash('You are not allowed to create users.', 'warning')
            return
        model = self.model(form.username.data, form.password.data, form.admin.data)
        form.populate_obj(model)
        self.session.add(model)
        self._on_model_change(form, model, True)
        self.session.commit()

    def update_model(self, form, model):
        if 'U' not in current_user.roles:
            flash('You are not allowed to edit users.', 'warning')
            return
        form.populate_obj(model)
        if form.new_password.data:
            if form.new_password.data != form.confirm.data:
                flash('Passwords must match')
                return
            model.pwdhash = generate_password_hash(form.new_password.data)
        self.session.add(model)
        self._on_model_change(form, model, False)
        self.session.commit()

    def delete_model(self, model):
        if 'D' not in current_user.roles:
            flash('You are not allowed to delete users.', 'warning')
            return
        super(UserAdminView, self).delete_model(model)

    def is_action_allowed(self, name):
        if name == 'delete' and 'D' not in current_user.roles:
            flash('You are not allowed to delete users.', 'warning')
            return False
        return True


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
