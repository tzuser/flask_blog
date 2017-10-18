from flask_wtf import Form
from wtforms import StringField,TextAreaField
from wtforms.validators import DataRequired,Length

class CommentForm(Form):
    LANGUAGES = ['zh']
    name = StringField(
        '昵称',
        validators=[DataRequired(),Length(max=255)]
    )
    text = TextAreaField(u'评论',validators=[DataRequired()])