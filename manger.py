from flask_script import Manager, Server
from webapp import create_app
from webapp.models import db,User,Post,Comment,Tag,tags
app=create_app('webapp.config.DevConfig')
manager = Manager(app)
manager.add_command('server',Server())
db.init_app(app)

@manager.shell
def make_shell_context():
    return dict(app=app,db=db,User=User,Post=Post,Tag=Tag,tags=tags,Comment=Comment)

if __name__ =="__main__":
    manager.run()