from flask_sqlalchemy import SQLAlchemy
from webapp.extensions import bcrypt
from flask_login import AnonymousUserMixin

db = SQLAlchemy()

roles = db.Table('role_users',
                 db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                 db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                 )

tags = db.Table('post_tags',
                db.Column('post_id', db.Integer(), db.ForeignKey('post.id')),
                db.Column('tag_id', db.Integer(), db.ForeignKey('tag.id'))
                )


class User(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    nickname = db.Column(db.String(20))
    head = db.Column(db.String(255))
    sex = db.Column(db.Integer())
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    roles = db.relationship('Role', secondary=roles, backref=db.backref('users', lazy='dynamic'))

    def __init__(self, username=None):
        self.username = username
        default = Role.query.filter_by(name="default").one()
        self.roles.append(default)

    def __repr__(self):
        return "<User '{}'>".format(self.username)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return str(self.id)


class Post(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    cover = db.Column(db.String(255))
    cover_width = db.Column(db.Integer())
    cover_height = db.Column(db.Integer())
    type = db.Column(db.String(20))
    summary = db.Column(db.String(500))
    text = db.Column(db.Text())
    read = db.Column(db.Integer(), default=0)
    video = db.Column(db.String(255))
    publish_date = db.Column(db.DateTime())
    update_date = db.Column(db.DateTime())
    post_hash = db.Column(db.String(255))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('posts', lazy='dynamic'))
    photos = db.relationship('Photo', backref="post", cascade='all, delete-orphan')

    def __init__(self, title=None):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)


class Photo(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    url = db.Column(db.String(255))
    width = db.Column(db.Integer())
    height = db.Column(db.Integer())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return "<Photo {}>".format(self.url)


class Tag(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title=None):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])


class Role(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)

class Download(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    hash = db.Column(db.String(255))
    url=db.Column(db.String(500))
    path=db.Column(db.String(255))

    def __repr__(self):
        return '<Download {}>'.format(self.hash)
