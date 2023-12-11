import datetime

from flask import request, render_template, flash, redirect, url_for, session, Blueprint, g
from flask_login import current_user, login_user, logout_user, login_required
from my_app import app, db, login_manager
from my_app.auth.models import User
from my_app.auth.forms import RegistrationForm, LoginForm


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
        flash(form.errors, 'danger')
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
