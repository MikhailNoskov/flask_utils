from functools import wraps

from flask import request, render_template, flash, redirect, url_for, session, Blueprint, g, abort
from flask_login import current_user, login_user, logout_user, login_required
from flask_dance.contrib.facebook import make_facebook_blueprint, facebook
from flask_dance.contrib.google import make_google_blueprint, google

from my_app import app, db, login_manager
from my_app.auth.models import User
from my_app.auth.forms import RegistrationForm, LoginForm, AdminUserCreateForm, AdminUserUpdateForm


auth_route = Blueprint('auth', __name__)


@auth_route.before_request
def get_current_user():
    g.user = get_current_user


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@auth_route.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in', 'info')
        return redirect(url_for('catalog.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_username = User.query.filter(User.username.like('%' + username + '%')).first()
        if existing_username:
            flash(
                'This username already exists. Try another one', 'warning'
            )
            return render_template('register.html', form=form)
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        flash(
            'You are registered successfully', 'success'
        )
        return redirect(url_for('catalog.home'))
    if form.errors:
        flash(f'{form.errors}', 'danger')
    return render_template('register.html', form=form)


@auth_route.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in', 'info')
        return redirect(url_for('catalog.home'))
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if not (existing_user and existing_user.check_password(password)):
            flash('Invalid username or password. Please try again.', 'danger')
            return render_template('login.html', form=form)
        login_user(existing_user, remember=True)  # Saves cookie after browser closed
        flash(
            'You have logged in successfully', 'success'
        )
        return redirect(url_for('catalog.home'))
    if form.errors:
        flash(form.errors, 'danger')
    return render_template('login.html', form=form)


@auth_route.route('/logout')
@login_required
def logout():
    # if 'username' in session:
    #     session.pop('username')
    #     flash('You have successfully logged out.', 'success')
    logout_user()
    return redirect(url_for('catalog.home'))


facebook_blueprint = make_facebook_blueprint(scope='email', redirect_to='auth_router.facebook_login')
google_blueprint = make_google_blueprint(
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to='google.login'
)


@auth_route.route("/facebook-login")
def facebook_login():
    if not facebook.authorized:
        return redirect(url_for("facebook.login"))

    resp = facebook.get("/me?fields=name,email")
    user = User.query.filter_by(username=resp.json()["email"]).first()
    if not user:
        user = User(resp.json()["email"], '')
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('Logged in as name=%s using Facebook login' % (resp.json()['name']), 'success' )
    return redirect(request.args.get('next', url_for('catalog.home')))


@auth_route.route("/google-login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v1/userinfo")
    user = User.query.filter_by(username=resp.json()["email"]).first()
    if not user:
        user = User(resp.json()["email"], '')
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('Logged in as name=%s using Google login' % (resp.json()['name']), 'success')
    return redirect(request.args.get('next', url_for('catalog.home')))


def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view


@auth_route.route('/admin')
@login_required
@admin_login_required
def home_admin():
    return render_template('admin-home.html')


@auth_route.route('/admin/users-list')
@login_required
@admin_login_required
def users_list_admin():
    users = User.query.all()
    return render_template('users-list-admin.html', users=users)


@auth_route.route('/admin/create-user', methods=['GET', 'POST',])
@login_required
@admin_login_required
def user_create_admin():
    form = AdminUserCreateForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        admin = form.admin.data
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash(
                'This username already exists. Try another one', 'warning'
            )
            return render_template('user-create-admin.html', form=form)
        user = User(username, password, admin)
        db.session.add(user)
        db.session.commit()
        flash(
            'New user created', 'success'
        )
        return redirect(url_for('auth.users_list_admin'))
    if form.errors:
        flash(f'{form.errors}', 'danger')
    return render_template('user-create-admin.html', form=form)


@auth_route.route('/admin/update-user/<id>', methods=['GET', 'POST',])
@login_required
@admin_login_required
def user_update_admin(id):
    user = User.query.get(id)
    form = AdminUserUpdateForm(
        username=user.username,
        admin=user.admin
    )
    if form.validate_on_submit():
        username = form.username.data
        admin = form.admin.data
        User.query.filter_by(id=id).update(
            {
                'username': username,
                'admin': admin
            }
        )
        db.session.commit()
        flash(
            'User updated', 'success'
        )
        return redirect(url_for('auth.users_list_admin'))
    if form.errors:
        flash(f'{form.errors}', 'danger')
    return render_template('user-update-admin.html', form=form, user=user)


@auth_route.route('/admin/delete-user/<id>')
@login_required
@admin_login_required
def user_delete_admin(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash(
        'User deleted', 'success'
    )
    return redirect(url_for('auth.users_list_admin'))
