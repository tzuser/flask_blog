from flask import abort,current_app
from flask_restful import Resource,marshal_with
from .parsers import user_post_parser,user_get_parser
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from webapp.models import User
from .post import user_fields

class AuthApi(Resource):
    @marshal_with(user_fields)
    def get(self):
        args = user_get_parser.parse_args()
        user=User.verify_auth_token(args['token'])

        if not user:
            abort(401)
        return user


    def post(self):
        args=user_post_parser.parse_args()
        user=User.query.filter_by(username=args['username']).first()

        if  not user:
            abort(401)

        if  user.check_password(args['password']):
            s=Serializer(current_app.config['SECRET_KEY'],expires_in=600)
            return {"token":s.dumps({"id": user.id}).decode('utf-8')}
        else:
            abort(401)
