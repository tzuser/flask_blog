from flask import Blueprint, flash, redirect, render_template, url_for
from webapp.forms import LoginForm, RegisterForm
from webapp.models import db, User

main_blueprint = Blueprint(
    'main',
    __name__,
    template_folder='../templates/main'
)


@main_blueprint.route('/')
def index():
    return '首页'


@main_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("登录成功!", category="success")
        return redirect(url_for('blog.home'))
    return render_template('login.html', form=form)


@main_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    flash("你已注销!", category="success")
    return redirect(url_for('blog.home'))


@main_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User()
        new_user.username = form.username.data
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash("注册成功，请登录！", category="success")
        return redirect(url_for('.login'))
    return render_template('register.html', form=form)
