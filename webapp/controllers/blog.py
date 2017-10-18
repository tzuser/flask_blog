from flask import  render_template, redirect, url_for, session, g, abort, Blueprint

from webapp.forms import CommentForm
from webapp.models import db, User, Post, Tag, Comment, tags
from sqlalchemy import func

import datetime


def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    top_tags = db.session.query(Tag, func.count(tags.c.post_id).label('total')).join(tags).group_by(Tag).order_by(
        'total DESC').limit(5).all()
    return recent, top_tags


blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder='../templates/blog',
    url_prefix="/blog"
)


@blog_blueprint.before_request
def before_request():
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@blog_blueprint.errorhandler(404)
def page_not_found(error):
    return "404错误"


@blog_blueprint.route('/home')
def home():
    posts = Post.query.limit(20).all()
    return render_template('home.html', posts=posts)


@blog_blueprint.route('/admin')
def admin():
    if g.user is None:
        abort(403)
    return render_template('admin.html')


@blog_blueprint.route('/post/<int:post_id>', methods=('GEt', 'POST'))
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        new_comment.date = datetime.datetime.now()
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('.post', post_id=post_id))
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    # recent,top_tags = sidebar_data()
    return render_template('blog/post.html',
                           post=post,
                           tags=tags,
                           comments=comments,
                           form=form)
