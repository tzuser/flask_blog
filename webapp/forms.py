from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, BooleanField, fields, IntegerField, SelectField, \
    HiddenField
from wtforms.validators import DataRequired, Length, EqualTo, URL
from webapp.models import User
from flask_login import current_user


class CommentForm(FlaskForm):
    LANGUAGES = ['zh']
    name = StringField(u'昵称', validators=[DataRequired(), Length(max=255)])
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
    nickname = StringField(u'昵称', [DataRequired()])
    sex = SelectField(u'性别', [DataRequired()], choices=[('1', '男'), ('2', '女')])
    head = StringField(u'头像')
    password = PasswordField(u'密码', [DataRequired(), Length(min=6)])
    confirm = PasswordField(u'确认密码', [DataRequired(), EqualTo('password')])

    def validate(self):
        check_validate = super(RegisterForm, self).validate()
        if not check_validate:
            return False
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user:
            self.nickname.errors.append('昵称已存在!')
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if user:
            self.username.errors.append('用户已存在!')
            return False

        return True


class PostForm(FlaskForm):
    title = StringField('标题', [DataRequired(), Length(max=255)])
    cover = StringField('封面')
    tags = StringField('标签')
    summary = TextAreaField('简介', [Length(max=500)])
    text = TextAreaField('内容')
    photos = fields.FieldList(StringField('图片'))
    video = StringField('视频')
    type = HiddenField('类型')

    def validate(self):
        check_validate = super(PostForm, self).validate()
        if not check_validate:
            return False

        if self.type.data == 'article' and (not self.text.data or self.text.data == '<p>&nbsp;</p>'):
            self.text.errors.append('文章内容未填写!')
            return False
        elif self.type.data == 'photo' and (not self.photos.data or self.photos.data==['']):
            self.photos.errors.append('图片未填写!')
            return False
        elif self.type.data == 'video' and not self.video.data:
            self.video.errors.append('视频未填写!')
            return False
        return True


class OpenIDForm(FlaskForm):
    openid = StringField('OpenID URL', [DataRequired(), URL()])


class SearchForm(FlaskForm):
    keyword = StringField(u'搜索', [DataRequired(), Length(max=30)])


class UserSettingForm(FlaskForm):
    nickname = StringField(u'昵称', [DataRequired()])
    sex = SelectField(u'性别', [DataRequired()], choices=[('1', '男'), ('2', '女')])
    head = StringField(u'头像', [DataRequired()])

    def validate(self):
        check_validate = super(UserSettingForm, self).validate()
        if not check_validate:
            return False
        user = User.query.filter_by(nickname=self.nickname.data).first()
        if user!=current_user and user:
            self.nickname.errors.append('昵称已存在!')
            return False
        return True
