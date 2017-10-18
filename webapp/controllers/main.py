from flask import Blueprint
main_blueprint=Blueprint('main',__name__,template_folder='../templates/main')
@main_blueprint.route('/')
def index():
    return '首页'