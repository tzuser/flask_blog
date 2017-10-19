from flask_wtf import Form
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, URL
from webapp.models import User


class CommentForm(Form):
    LANGUAGES = ['zh']
    name = StringField(
        u'昵称',
        validators=[DataRequired(), Length(max=255)]
    )
    text = TextAreaField(u'评论', validators=[DataRequired()])


class LoginForm(Form):
    username = StringField(u'用户名', [DataRequired(), Length(max=255)])
    password = PasswordField(u'密码', [DataRequired()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()
        if not check_validate:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append(u'用户不存在')
            return False
        if not user.check_password(self.password.data):
            self.password.errors.append(u'密码错误')
            return False

        return True


class RegisterForm(Form):
    username = StringField(u'用户名', [DataRequired(), Length(max=255)])
    password = PasswordField(u'密码', [DataRequired(), Length(min=6)])
    confirm = PasswordField(u'确认密码', [DataRequired(), EqualTo('password')])

    def validate(self):
        check_validate = super(RegisterForm, self).validate()
        if not check_validate:
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append('用户已存在!')
            return False
        
        return True

class PostForm(Form):
    title=StringField('Title',[DataRequired(),Length(max=255)])
    text=TextAreaField('Content',[DataRequired()])