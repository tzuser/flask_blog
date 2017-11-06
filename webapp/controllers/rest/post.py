from flask_restful import Resource,fields,marshal_with
from flask import abort
from webapp.models import Post,User
from .parsers import post_get_parser

user_fields={
    'id':fields.Integer(),
    'username':fields.String(),
    'nickname':fields.String(),
    'head':fields.String(),
    'sex':fields.Integer(),
}

tag_fields={
    'id':fields.Integer(),
    'title':fields.String()
}

photo_fields={
    'id':fields.Integer(),
    'url':fields.String()
}

post_fields={
    'title':fields.String(),
    'text':fields.String(),
    'type':fields.String(),
    'cover':fields.String(),
    'publish_date':fields.DateTime(dt_format='iso8601'),
    'video':fields.String(),
    'tags':fields.List(fields.Nested(tag_fields)),
    'photos':fields.List(fields.Nested(photo_fields)),
    'user':fields.Nested(user_fields)
}
class PostApi(Resource):
    @marshal_with(post_fields)
    def get(self,post_id=None):
        if post_id:
            post=Post.query.get(post_id)
            print(post.photos)
            if not post:
                abort(404)
            return post
        else:
            args=post_get_parser.parse_args()
            page=args['page']

            if args['user']:
                user=User.query.filter_by(username=args['user']).first()
                if not user:
                    abort(404)
                posts=user.posts.order_by(Post.publish_date.desc()).paginate(page,10)
            else:
                posts=Post.query.order_by(
                    Post.publish_date.desc()
                ).filter(Post.status==0).paginate(page,10)

            return posts.items