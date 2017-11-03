from flask import render_template, redirect, url_for, session, g, abort, Blueprint, flash, request

from webapp.forms import CommentForm, PostForm, SearchForm
from webapp.models import db, User, Post, Tag, Comment, tags, Photo
from sqlalchemy import func
from flask_login import login_required, current_user
from flask_principal import Permission, UserNeed
from webapp.extensions import poster_permission, admin_permission

from datetime import datetime


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
    g.tags = Tag.query.limit(20).all()
    g.is_login = hasattr(current_user, 'id')  # 是否登录


@blog_blueprint.errorhandler(404)
def page_not_found(error):
    return "404错误"


@blog_blueprint.errorhandler(403)
def page_not_found(error):
    return "你没有权限"


@blog_blueprint.route('/home')
def home():
    posts = Post.query.order_by(Post.publish_date.desc()).limit(20).all()
    return render_template('home.html', posts=posts)


@blog_blueprint.route('/admin')
def admin():
    if g.user is None:
        abort(403)
    return render_template('admin.html')


@blog_blueprint.route('/new/<string:type>', methods=['GET', 'POST'])
@login_required
def new(type):
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(form.title.data)
        new_post.text = form.text.data
        new_post.cover = form.cover.data
        new_post.publish_date = datetime.datetime.now()
        new_post.update_date = new_post.publish_date
        new_post.user_id = current_user.id
        new_post.type = type
        new_post.summary = form.summary.data
        new_post.video = form.video.data
        tagStrList = form.tags.data.split(',')
        for tagStr in tagStrList:
            tagStr = tagStr.strip()
            tag = Tag.query.filter_by(title=tagStr).first()
            if not tag:
                tag = Tag(tagStr)
            new_post.tags.append(tag)

        for photo_url in form.photos.data:
            if photo_url != '':
                photo = Photo(photo_url)
                new_post.photos.append(photo)

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('blog.post', post_id=new_post.id))
    form.type.data = type
    return render_template("edit_{}.html".format(type), form=form, type=type)

@blog_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@poster_permission.require(http_exception=403)
def edit(id):
    post = Post.query.get_or_404(id)
    permission = Permission(UserNeed(post.user.id))
    if permission.can() or admin_permission.can():
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.cover = form.cover.data
            post.video = form.video.data
            post.summary = form.summary.data
            post.text = form.text.data
            post.update_date = datetime.now()
            del post.tags[:]  # 删除所有标签
            del post.photos[:]  # 删除所有图片

            if form.tags.data.strip():
                tagStrList = form.tags.data.split(',')
                for tagStr in tagStrList:  # 对标签循环
                    tagStr = tagStr.strip()
                    tag = Tag.query.filter_by(title=tagStr).first()
                    if not tag:  # 标签不存在时新增
                        tag = Tag(tagStr)
                    post.tags.append(tag)

            for photo_url in form.photos.data:
                if photo_url != '':
                    photo = Photo(photo_url)
                    post.photos.append(photo)

            db.session.add(post)
            db.session.commit()
            return redirect(url_for('.post', post_id=post.id))
        type = post.type
        form.cover.data = post.cover
        form.text.data = post.text
        form.title.data = post.title
        form.summary.data = post.summary
        form.type.data = type
        photos = [photo.url for photo in post.photos]
        form.summary.data = post.summary
        tags = []
        for tag in post.tags:
            tags.append(tag.title)
        form.tags.data = ','.join(tags)

        return render_template("edit_{}.html".format(type), form=form, post=post, photos=photos)
    abort(403)


@blog_blueprint.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post(post_id):
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        new_comment.date = datetime.now()
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('.post', post_id=post_id))
    post = Post.query.get_or_404(post_id)
    # 添加阅读量
    post.read = post.read + 1
    db.session.add(post)
    db.session.commit()

    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    # 是否有编辑权限
    permission = Permission(UserNeed(post.user.id))
    is_edit = permission.can() or admin_permission.can()
    if g.is_login:
        form.name.data = current_user.username
    return render_template('post.html',
                           post=post,
                           tags=tags,
                           is_edit=is_edit,
                           comments=comments,
                           form=form)


@blog_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    form = g.search_form
    if form.validate_on_submit():
        posts = Post.query.filter(Post.title.ilike("%{}%".format(form.keyword.data))).all()
        return render_template('search.html', posts=posts)
    return redirect(url_for('blog.home'))


@blog_blueprint.route('/tag/<int:id>', methods=['GET'])
def tag(id):
    tag = Tag.query.get_or_404(id)
    posts = tag.posts.all()
    return render_template('search.html', posts=posts)


@blog_blueprint.route('/list/<string:type>/<string:order>/<int:count>/<int:page>', methods=['GET'])
def list(type, order, count, page):
    if type=="all":
        pageData = Post.query.order_by(getattr(Post, order).desc()).paginate(page, count)
    else:
        pageData = Post.query.order_by(getattr(Post,order).desc()).filter_by(type=type).paginate(page, count)
    return render_template('list.html', type=type,order=order,page=pageData, count=count)
