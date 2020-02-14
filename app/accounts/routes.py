from app import db, bcrypt
from flask import render_template, redirect, flash, url_for, request, Blueprint
from flask_login import current_user, login_user, login_required, logout_user
from app.users.models import User
from app.accounts.forms import RegisterForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from app.accounts.utils import send_reset_email


accounts = Blueprint('accounts',  __name__)


@accounts.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash('Akun anda berhasil dibuat! silahkan login!', 'success')
        return redirect(url_for('accounts.login'))

    return render_template('register.html', form=form)


@accounts.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))

        flash('Login gagal!', 'danger')

    return render_template('login.html', form=form)


@accounts.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('accounts.login'))


@accounts.route('/dashboard/account', methods=['GET', 'POST'])
@login_required 
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.password.data != '':
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
        db.session.commit()

        flash('Akun anda berhasil diubah!', 'success')
        return redirect(url_for('accounts.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    return render_template('account.html', title="Akun", form=form)


@accounts.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
       return redirect(url_for('main.dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Email telah dikirim untuk reset password anda!', 'info')
        return redirect(url_for('accounts.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@accounts.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
       return redirect(url_for('main.dashboard'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('Token is invalid or expired!', 'warning')
        return redirect(url_for('accounts.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.add(user)
        db.session.commit()
        flash('Password anda berhasil direset! silahkan login!', 'success')
        return redirect(url_for('accounts.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)