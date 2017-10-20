from flask import render_template, redirect, url_for, session, g, abort, Blueprint,flash

from webapp.forms import CommentForm, PostForm,SearchForm
from webapp.models import db, User, Post, Tag, Comment, tags
from sqlalchemy import func
from flask_login import login_required,current_user
from flask_principal import Permission,UserNeed
from webapp.extensions import poster_permission,admin_permission

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
    g.search_form = SearchForm()
    g.tags = Tag.query.all()

@blog_blueprint.errorhandler(404)
def page_not_found(error):
    return "404错误"


@blog_blueprint.route('/home')
def home():
    posts = Post.query.order_by(Post.publish_date.desc()).limit(20).all()
    return render_template('home.html', posts=posts)


@blog_blueprint.route('/admin')
def admin():
    if g.user is None:
        abort(403)
    return render_template('admin.html')


@blog_blueprint.route('/new', methods=('GET', 'POST'))
@login_required
def new():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(form.title.data)
        new_post.text = form.text.data
        new_post.publish_date = datetime.datetime.now()
        new_post.user_id=current_user.id
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog.post', post_id=new_post.id))
    return render_template('new.html', form=form)


@blog_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@poster_permission.require(http_exception=403)
def edit(id):

    post = Post.query.get_or_404(id)
    permission=Permission(UserNeed(post.user.id))
    if permission.can() or admin_permission.can():
        # if not (current_user.is_active and current_user==post.user):
        #     flash("你没有权限!", category="danger")
        #     return redirect(url_for('.home'))
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.text = form.text.data
            post.publish_date = datetime.datetime.now()

            db.session.add(post)
            db.session.commit()
            return redirect(url_for('.post', post_id=post.id))
        form.text.data = post.text
        return render_template('edit.html', form=form, post=post)
    abort(403)


@blog_blueprint.route('/post/<int:post_id>', methods=('GET', 'POST'))
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

    if current_user.is_active:
        form.name.data=current_user.username
    return render_template('post.html',
                           post=post,
                           tags=tags,
                           comments=comments,
                           form=form)

@blog_blueprint.route('/search',methods=['GET','POST'])
def search():
    form=g.search_form
    if form.validate_on_submit():
        posts=Post.query.filter(Post.title.ilike("%{}%".format(form.keyword.data))).all()
        return render_template('search.html',posts=posts)
    return redirect(url_for('blog.home'))

@blog_blueprint.route('/tag/<int:id>',methods=['GET'])
def tag(id):
    tag=Tag.query.get_or_404(id)
    posts=tag.posts.all()
    return render_template('search.html',posts=posts)
