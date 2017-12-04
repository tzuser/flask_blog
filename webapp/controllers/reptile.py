from flask import render_template, redirect, url_for, session, g, abort, Blueprint, flash, request
from webapp.models import db, User, Post, Tag, Comment, tags, Photo,Download
import json, time,os
import datetime
from sqlalchemy.sql import or_
import urllib
reptile_blueprint = Blueprint(
    'reptile',
    __name__,
    template_folder='../templates/reptile',
    url_prefix="/reptile"
)


@reptile_blueprint.route('/new_post', methods=['POST'])
def new_post():
    if request.method == 'POST':
        jsonStr = request.get_data()
        data = json.loads(jsonStr)
        if hasattr(data, 'key') or data['key'] != "wysj3910":
            return "密钥错误!"
        new_post = Post(data['title'])  # 创建帖子
        new_post.text = data['text']  # 内容
        new_post.cover = data['cover']  # 封面
        new_post.publish_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(data['publish_date']))  # 发布日期
        new_post.update_date = datetime.datetime.now()#更新的日期
        user = User.query.filter_by(username=data['username']).first()  # 获取用户
        if not user:
            user = User(data['username'])
            if hasattr(data,'nickname'):
                user.nickname=data['nickname']
        new_post.user = user  # 用户
        new_post.type = data['type']  # 类型
        new_post.summary = data['summary']  # 简介
        new_post.video = data['video']  # 视频地址
        new_post.read = data['read']  # 阅读量
        new_post.post_hash=data['post_hash'] #贴的hash值
        for photo_url in data['photos']:  # 图片列表
            if photo_url != '':
                photo = Photo(photo_url)
                new_post.photos.append(photo)

        for tagStr in data['tags']:  # 标签
            tagStr = tagStr.strip()
            tag = Tag.query.filter_by(title=tagStr).first()
            if not tag:
                tag = Tag(tagStr)
            new_post.tags.append(tag)
        db.session.add(new_post)
        db.session.commit()
        return json.dumps({'status':0})

#帖子是否存在
@reptile_blueprint.route('/is_post/<string:post_hash>', methods=['GET'])
def is_post(post_hash):
    post=Post.query.filter_by(post_hash=post_hash).first()
    status=0
    if not post:
        status=1
    return json.dumps({'status':status})


#保存下载文件信息
@reptile_blueprint.route('/add_download', methods=['POST'])
def add_download():
    if request.method == 'POST':
        jsonStr = request.get_data()
        data = json.loads(jsonStr)
        if hasattr(data, 'key') or data['key'] != "wysj3910":
            return "密钥错误!"
        dl=Download()
        dl.hash=data['hash']
        dl.url = data['url']
        dl.path = data['path']
        db.session.add(dl)
        db.session.commit()
        return json.dumps({'status':0})

#文件是否存在
@reptile_blueprint.route('/is_download', methods=['POST'])
def is_download():
    if request.method == 'POST':
        jsonStr = request.get_data()
        data = json.loads(jsonStr)
        dl=Download.query.filter(or_(Download.hash==data['hash'],Download.path==data['path'])).first()
        if not dl:
            return json.dumps({'status':1})
        return json.dumps({'status': 0, 'path': dl.path})

@reptile_blueprint.route('/upload', methods=['POST'])
def uploaduploadupload():
    file = request.files['file']
    filename=request.form.get('filename')
    path=f"./webapp{filename[0:filename.rfind('/')+1]}"
    name=filename[filename.rfind('/')+1:]
    # 创建下载目录
    if not os.path.exists(path):
        os.makedirs(path)
    savePath=f"{path}{name}"
    file.save(savePath)
    return  json.dumps({'status': 0, 'message':'上传成功!','path':savePath})
