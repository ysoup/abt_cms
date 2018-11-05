import os
basedir = os.path.abspath(os.path.dirname(__file__))


class config:
    VALID_URL = ['/login',]
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'this is a secret string'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/user'
    SQLALCHEMY_BINDS = {
        'permission_manage': '',
        "spiders_visualization": ""}
    BANNER_DETAIL_URL = ''
    REDIS_URL = ""
    REQUEST_URL = ""
    # 搜索引擎设置
    SP_HOST = ''
    SP_PORT = 9312
    # PAPER_LOAD = "http://back-test.aibilink.com/download_rep"
    KLINE = ""



class TestingConfig(config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'test')


class OpentingConfig(config):
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_BINDS = {'permission_manage': '',}
    BANNER_DETAIL_URL = ''
    REDIS_URL = ""
    REQUEST_URL = ""
    # 搜索引擎设置
    SP_HOST = ''
    SP_PORT = 9312
    # PAPER_LOAD = "https://backend.aibilink.com/download_rep"
    KLINE = ""

class ProductionConfig(config):
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_BINDS = {
        'permission_manage': '',
        "spiders_visualization": ""}
    BANNER_DETAIL_URL = ''
    REDIS_URL = ""
    REQUEST_URL = ""
    # 搜索引擎设置
    SP_HOST = ''
    SP_PORT = 9312
    KLINE = ""



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'open': OpentingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}