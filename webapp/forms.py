from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField , fields
from wtforms.validators import DataRequired, Length, EqualTo, URL
from webapp.models import User

class CommentForm(FlaskForm):
    LANGUAGES = ['zh']
    name = StringField(u'昵称',validators=[DataRequired(), Length(max=255)])
    text = TextAreaField(u'评论', validators=[DataRequired()])


class LoginForm(FlaskForm):
    username = StringField(u'用户名', [DataRequired(), Length(max=255)])
    password = PasswordField(u'密码', [DataRequired()])
    remember = BooleanField(u'记住我')
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


class RegisterForm(FlaskForm):
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

class PostForm(FlaskForm):
    title=StringField('标题',[DataRequired(),Length(max=255)])
    cover=StringField('封面')
    tags=StringField('标签')
    text=TextAreaField('内容',[DataRequired()])
    photos=fields.FieldList(StringField('图片'))

class OpenIDForm(FlaskForm):
    openid=StringField('OpenID URL',[DataRequired(),URL()])

class SearchForm(FlaskForm):
    keyword=StringField(u'搜索',[DataRequired(),Length(max=30)])