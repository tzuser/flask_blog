from flask import Flask,render_template,redirect,url_for
# from webapp.config import DevConfig
# from webapp.extensions import bcrypt
# from webapp.forms import CommentForm
# from webapp.models import db,User,Post,Tag,Comment,tags
from webapp.config import DevConfig
from webapp.extensions import bcrypt
from webapp.forms import CommentForm
from webapp.models import db,User,Post,Tag,Comment,tags

import datetime

def create_app(object_name):
    app = Flask(__name__)
    app.config.from_object(object_name)
    db.init_app(app)

    @app.route('/')
    @app.route('/home')
    def home():
        posts=Post.query.limit(20).all()
        return render_template('home.html',posts=posts)

    @app.route('/post/<int:post_id>',methods=('GEt','POST'))
    def post(post_id):
        form = CommentForm()
        if form.validate_on_submit():
            new_comment = Comment()
            new_comment.name=form.name.data
            new_comment.text=form.text.data
            new_comment.post_id=post_id
            new_comment.date=datetime.datetime.now()
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('post',post_id=post_id))
        post=Post.query.get_or_404(post_id)
        tags=post.tags
        comments=post.comments.order_by(Comment.date.desc()).all()
        #recent,top_tags = sidebar_data()
        return render_template('post.html',
                               post=post,
                               tags=tags,
                               comments=comments,
                               form=form)
    return app


