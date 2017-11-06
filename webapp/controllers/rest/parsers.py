from flask_restful import reqparse

post_get_parser=reqparse.RequestParser()
post_get_parser.add_argument(
    'page',
    type=int,
    default=1,
    location=['json','args','headers'],
    required=False)
post_get_parser.add_argument(
    'user',
    type=str,
    location=['json','args','headers']
)





user_post_parser=reqparse.RequestParser()
user_post_parser.add_argument('username',type=str,required=True)
user_post_parser.add_argument('password',type=str,required=True)