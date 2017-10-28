from flask import Blueprint, flash, redirect, render_template, url_for,current_app
from webapp.extensions import oid
from webapp.forms import LoginForm, RegisterForm,OpenIDForm,UserSettingForm
from webapp.models import db, User
from flask_login import login_user,logout_user,login_required,current_user
from flask_principal import (Identity,AnonymousIdentity,identity_changed)

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='../templates/main'
)


@main_blueprint.route('/')
def index():
    return '首页'


@main_blueprint.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    form = LoginForm()
    openid_form = OpenIDForm()
    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname','email'],
            ask_for_optional=['fullname']
        )

    if form.validate_on_submit():
        user=User.query.filter_by(username=form.username.data).first()
        login_user(user,remember=form.remember.data)

        identity_changed.send(
            current_app._get_current_object(),
            identity=Identity(user.id)
        )
        flash("登录成功!", category="success")
        return redirect(url_for('blog.home'))

    openid_errors=oid.fetch_error()
    if openid_errors:
        flash(openid_errors,category="danger")
    form.remember.data=True
    return render_template('login.html', form=form,openid_form=openid_form)


@main_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    identity_changed.send(
        current_app._get_current_object(),
        identity=AnonymousIdentity()
    )
    flash("你已注销!", category="success")
    return redirect(url_for('blog.home'))


@main_blueprint.route('/register', methods=['GET', 'POST'])
@oid.loginhandler
def register():
    form = RegisterForm()
    openid_form=OpenIDForm()
    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname','email'],
            ask_for_optional=['fullname']
        )
    if form.validate_on_submit():
        new_user = User()
        new_user.username = form.username.data
        new_user.nickname = form.nickname.data
        new_user.sex = form.sex.data
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("注册成功，请登录！", category="success")
        return redirect(url_for('.login'))

    openid_errors=oid.fetch_error()
    if openid_errors:
        flash(openid_errors,category="danger")

    return render_template('register.html', form=form , openid_form=openid_form)


@main_blueprint.route('/user_setting', methods=['GET', 'POST'])
@login_required
def user_setting():
    form = UserSettingForm()
    user=current_user
    if form.validate_on_submit():
        user.nickname=form.nickname.data
        user.sex=form.sex.data
        user.head=form.head.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('blog.home'))
    form.sex.default=user.sex
    form.process()
    form.nickname.data=user.nickname
    form.head.data=user.head
    return render_template('user_setting.html', form=form )

