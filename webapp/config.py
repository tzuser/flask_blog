class Config(object):
    pass
class ProdConfig(Config):
    pass
class DevConfig(Config):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI ='sqlite:///../database.db'#'mysql+pymysql://root:wysj3910@localhost:3306/web' #'sqlite:///../database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'tzuser'
    LANGUAGES = ['zh-CN', 'zh']