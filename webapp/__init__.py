from flask import Flask,redirect,url_for
from webapp.config import DevConfig
from webapp.extensions import bcrypt
from webapp.forms import CommentForm
from webapp.models import db,User,Post,Tag,Comment,tags
from webapp.controllers.blog import blog_blueprint
from webapp.controllers.main import main_blueprint

def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)

    db.init_app(app)

    @app.route('/')
    def index():
        return redirect(url_for('blog.home'))

    app.register_blueprint(main_blueprint)
    app.register_blueprint(blog_blueprint)
    return app
