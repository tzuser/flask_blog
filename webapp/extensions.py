from flask_bcrypt import Bcrypt
from flask_openid import OpenID
from flask import flash,redirect,url_for
from flask_login import LoginManager


bcrypt=Bcrypt()
oid=OpenID()

login_manager=LoginManager()
login_manager.login_view="main.login"
login_manager.session_protection="strong"
login_manager.login_message=u"请登录访问此页面"
login_manager.login_message_category="info"

@login_manager.user_loader
def load_user(userid):
    from webapp.models import User
    return User.query.get(userid)

@oid.after_login
def create_or_login(resp):
    from webapp.models import db,User
    username=resp.fullname or resp.nickname or resp.email
    if not username:
        flash('Invalid login. please try again.','danger')
        return redirect(url_for('main.login'))
    user=User.query.filter_by(username=username).first()
    if user is None:
        user=User(username)
        db.session.add(user)
        db.session.commit()
    # 在这登录用户
    return redirect(url_for('blog.home'))