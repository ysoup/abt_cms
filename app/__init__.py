from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from flask_redis import FlaskRedis
import logging

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = current_app.config["SQLALCHEMY_DATABASE_URI"]


db = SQLAlchemy()
redis_store = FlaskRedis()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_POOL_SIZE'] = 50
    app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
    app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 30
    config[config_name].init_app(app)
    redis_store.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)
    file_handler = logging.FileHandler('cms_error.log')
    logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    file_handler.setFormatter(logging_format)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)

    # 快讯
    from .new_flash import new_flash as new_flash_blueprint
    app.register_blueprint(new_flash_blueprint)

    # main
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # 用户
    from .auh import user_b as user_blueprint
    app.register_blueprint(user_blueprint)

    # # 活动
    # from .activity import act as act_blueprint
    # app.register_blueprint(act_blueprint)
    #
    # # 早晚报
    # from .report import rep as rep_blueprint
    # app.register_blueprint(rep_blueprint)
    #
    # # 研究报告
    # from .research_paper import research_paper as research_paper_blueprint
    # app.register_blueprint(research_paper_blueprint)
    #
    # # 日历管理
    # from .calendar import cal as cal_blueprint
    # app.register_blueprint(cal_blueprint)
    #
    # # 爬虫管理
    # from .crawler import crawl as crawl_blueprint
    # app.register_blueprint(crawl_blueprint)
    #
    # # F10
    # from .ften import ft as f10_blueprint
    # app.register_blueprint(f10_blueprint)
    #
    # # 星球相关
    # from .planet import planet as pt_blueprint
    # app.register_blueprint(pt_blueprint)
    #
    # # 客户管理
    # from .customers import customer as cus_blueprint
    # app.register_blueprint(cus_blueprint)
    #
    # # 星球币相关
    # from .planet_token_manage import planet_token as planet_token_blueprint
    # app.register_blueprint(planet_token_blueprint)
    #
    # # 版本相关
    # from .sys_version import version as version_blueprint
    # app.register_blueprint(version_blueprint)

    # 账户
    # from .account_info import account as account_blueprint
    # app.register_blueprint(account_blueprint)

    return app