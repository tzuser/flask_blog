from flask import Flask,redirect,url_for,g
from .config import DevConfig
from .extensions import bcrypt,oid,login_manager,principal,rest_api
from .models import db,User,Post,Tag,Comment,tags
from .controllers.blog import blog_blueprint
from .controllers.main import main_blueprint
from .controllers.reptile import reptile_blueprint
from flask_login import current_user
from flask_principal import identity_loaded,UserNeed,RoleNeed
from .controllers.rest.post import PostApi
from .controllers.rest.auth import AuthApi
#跨域
from flask_cors import CORS

def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)
    #跨域
    CORS(app, supports_credentials=True)

    db.init_app(app)
    bcrypt.init_app(app)
    oid.init_app(app)
    login_manager.init_app(app)
    principal.init_app(app)

    # RESTapi
    rest_api.add_resource(PostApi, '/api/post','/api/post/<int:post_id>',endpoint='api')
    rest_api.add_resource(AuthApi, '/api/auth')
    rest_api.init_app(app)

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

    app.register_blueprint(main_blueprint)#系统
    app.register_blueprint(blog_blueprint)#博客
    app.register_blueprint(reptile_blueprint)#爬虫

    return app
