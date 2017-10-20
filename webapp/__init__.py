from flask import Flask,redirect,url_for,g
from webapp.config import DevConfig
from webapp.extensions import bcrypt,oid,login_manager,principal
from webapp.models import db,User,Post,Tag,Comment,tags
from webapp.controllers.blog import blog_blueprint
from webapp.controllers.main import main_blueprint
from flask_login import current_user
from flask_principal import identity_loaded,UserNeed,RoleNeed


def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)

    db.init_app(app)
    bcrypt.init_app(app)
    oid.init_app(app)
    login_manager.init_app(app)
    principal.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender,identity):
        identity.user=current_user

        if hasattr(current_user,'id'):
            identity.provides.add(UserNeed(current_user.id))

        if hasattr(current_user,'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))



    @app.route('/')
    def index():
        return redirect(url_for('blog.home'))

    app.register_blueprint(main_blueprint)
    app.register_blueprint(blog_blueprint)
    return app
