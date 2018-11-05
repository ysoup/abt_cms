import datetime, time
from cms_server import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from . import login_manager
from sqlalchemy.orm import relationship


# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
#
# class User(UserMixin, db.Model):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key = True)
#     email = db.Column(db.String(64), unique=True, index=True)
#     username = db.Column(db.String(64), unique=True, index=True)
#     password_hash = db.Column(db.String(128))
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

# 用户
# class UserInfo(db.Model):
#     password_hash = db.Column(db.String(128))
#
#     @property
#     def password(self):
#         raise AttributeError('password is not a readable attribute')
#
#     @password.setter
#     def password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#     def verify_password(self, password):
#         return check_password_hash(self.password_hash, password)


# 快讯
class NewFlashInformation(db.Model):
    __tablename__ = 'new_flash_information'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer)
    content = db.Column(db.String(4000))
    title = db.Column(db.String(500))
    author = db.Column(db.String(128))
    source_name = db.Column(db.String(500), default="")
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    category = db.Column(db.Integer,db.ForeignKey('new_flash_category.id'), nullable=True)
    flash_cate = relationship("NewFlashCategory", backref="new_flash_ifm")
    is_show = db.Column(db.Integer, default=1)
    is_push = db.Column(db.Integer, default=0)
    is_delete = db.Column(db.Integer, default=0)
    remarks = db.Column(db.String(512), default="")
    highlight_color = db.Column(db.Integer, default=0)
    info_id = db.Column(db.Integer, db.ForeignKey('new_flash_exclusive_information.content_id'), nullable=True)
    info = relationship("NewInformation",backref='new_flash_ifm')
    possible_similarity = db.Column(db.Integer, default=0)

# 定制快讯规则
class NewFlashRule(db.Model):
    __tablename__ = 'new_flash_rule'
    id = db.Column(db.Integer, primary_key=True)
    origin_name = db.Column(db.String(128), default="")
    rule_name = db.Column(db.String(128), default="")
    create_name = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now)
    is_delete = db.Column(db.Integer, default=0)

# 快讯类别
class NewFlashCategory(db.Model):
    __tablename__ = 'new_flash_category'
    id = db.Column(db.Integer, primary_key=True)
    catname = db.Column(db.String(20), unique=True)
    is_show = db.Column(db.Integer, default=1)
    is_delete = db.Column(db.Integer, default=0)
    keyword = db.Column(db.String(300), default="")

# 资讯
class NewInformation(db.Model):
    __tablename__ = 'new_flash_exclusive_information'
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer)
    content = db.Column(db.String(4000))
    title = db.Column(db.String(500), default="")
    author = db.Column(db.String(128), default="")
    source_name = db.Column(db.String(500), default="")
    img = db.Column(db.String(128), default="")
    tag = db.Column(db.Integer, default="")
    is_show = db.Column(db.Integer, default=1)
    is_push = db.Column(db.Integer, default=0)
    is_delete = db.Column(db.Integer, default=0)
    remarks = db.Column(db.String(512), default="")
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now)
    category = db.Column(db.Integer, db.ForeignKey('news_category.id'), nullable=True)
    info_cate = relationship("InformationCategory", backref='info')
    source_url = db.Column(db.String(256), default="")
    foot_bar_id = db.Column(db.Integer, db.ForeignKey("foot_bar.id") ,default=0)
    foot_bar = db.relationship("FootBar", backref="footbar_obj", lazy="joined")
    content_type = db.Column(db.Integer, default=0)     #  0:抓取资讯;1:原创;2:解盘;3:视频;4:音频;5:pdf;6:早报;7:晚报

    # top_source_id = db.Column(db.Integer, db.ForeignKey('index_source.id'))
    # top_source = db.relationship("IndexSource", backref='report_top', foreign_keys=[top_source_id])
    # possible_similarity = db.Column(db.Integer, default=0)



# class FootBar(db.Model):
#     __tablename__ = "foot_bar"
#     id = db.Column(db.Integer, primary_key=True)
#     content = db.Column(db.String(2048),default="", nullable=False)
#     is_delete = db.Column(db.Integer, default=0)

# 资讯类别
class InformationCategory(db.Model):
    __tablename__ = 'news_category'
    id = db.Column(db.Integer, primary_key=True)
    catname = db.Column(db.String(20), unique=True, default="")
    is_show = db.Column(db.Integer, default=1)
    is_delete = db.Column(db.Integer, default=0)
    keyword = db.Column(db.String(600), default="")

# Banner
class Banner(db.Model):
    __tablename__ = 'news_banner_list'
    id = db.Column(db.Integer, primary_key=True)
    banner_name = db.Column(db.String(128), nullable=True, default='')
    banner_desc = db.Column(db.String(300), nullable=True, default='')
    banner_img = db.Column(db.String(300), nullable=True, default='')
    is_show = db.Column(db.Integer, default=0)
    is_delete = db.Column(db.Integer, default=0)
    skip_url = db.Column(db.String(128), nullable=True, unique=True, default='')
    putaway_time = db.Column(db.DateTime)

# 用户
class User(UserMixin,db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), unique=True, index=True, nullable=True)
    phone_no = db.Column(db.Integer, unique=True, index=True, nullable=True)
    password = db.Column(db.String(32), default=123)
    last_seen = db.Column(db.DATETIME(), default=datetime.datetime.now)  # 上次访问时间

    def __repr__(self):
        return  self.email or self.phone_no

# rep_source_sec = db.Table("rep_source_sec",
#                       db.Column("report_id", db.Integer, db.ForeignKey('report.id'), primary_key=True),
#                       db.Column('source_id', db.Integer, db.ForeignKey('index_source.id'), primary_key=True)
#                       )

class Rep2Source(db.Model):
    __tablename__  = "rep_source_sec"
    report_id = db.Column(db.Integer, db.ForeignKey("report.id"), primary_key=True)
    source_id = db.Column(db.Integer, db.ForeignKey("index_source.id"), primary_key=True)

class Report(db.Model):
    """早晚报"""
    __tablename__ = "report"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.Integer, default=1)
    content = db.Column(db.String(3072), default="")
    title = db.Column(db.String(256), default="")
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    is_delete = db.Column(db.Integer, default=0)
    information_id = db.Column(db.Integer)

    top_source_id = db.Column(db.Integer, db.ForeignKey('index_source.id'))
    top_source = db.relationship("IndexSource", backref='report_top', foreign_keys=[top_source_id])
    # rep和source产生关联
    # 因为rep和source表中间还有一rep_source表,所以添加secondary
    # 假如拿到了一个标签IndexSource,怎么拿到标签下的所有rep呢.反向引用rep这时用backref
    sec_source = db.relationship('IndexSource',secondary= "rep_source_sec",backref = db.backref('rep_sec'))

class IndexSource(db.Model):
    """指数来源"""
    __tablename__ = "index_source"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_name = db.Column(db.String(512), default="")
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    is_delete = db.Column(db.Integer, default=0)

class ViewNoticeList(db.Model):
    """通知栏信息"""
    __tablename__ = "view_notice_list"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    original_id = db.Column(db.Integer)
    original_img = db.Column(db.String(128), default="")
    original_type = db.Column(db.Integer)
    is_userful = db.Column(db.Integer, default=1)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    present_date = db.Column(db.String(128))


#################################### 日历相关 #########################################

class Event2News(db.Model):
    __tablename__ = "event_to_news"
    event_id = db.Column(db.Integer, db.ForeignKey("calendar_event.id"), primary_key=True)
    news_id = db.Column(db.Integer, db.ForeignKey("new_flash_information.id"), primary_key=True)

class Event2Info(db.Model):
    __tablename__ = "event_to_info"
    event_id = db.Column(db.Integer, db.ForeignKey("calendar_event.id"), primary_key=True)
    info_id = db.Column(db.Integer, db.ForeignKey("new_flash_exclusive_information.id"), primary_key=True)

class Events(db.Model):
    """事件表"""
    __tablename__ = "calendar_event"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    content = db.Column(db.String(1000), default="", comment="事件内容")
    happened_date = db.Column(db.Date, default=time.strftime("%Y-%m-%d", time.localtime()), comment="事件发生日期")
    # happened_time =db.Column(db.Time, default=time.strftime("%H:%M", time.localtime()), comment="事件发生时间")
    happened_time =db.Column(db.Time, nullable=True, comment="事件发生时间")
    happened_tag_type = db.Column(db.Integer, default=1, comment="关联事件标签类型：1. 地区; 2. 币种; 3. 交易所")
    happened_tag_id = db.Column(db.Integer, default=1, comment="关联事件标签类型下的ID")
    importance = db.Column(db.String(16),default="1", comment="事件重要程度：'1','2''3'级")
    # subject_id = db.Column(db.Integer, comment="关联的主题ID")
    keywords = db.Column(db.String(100), default="", comment="事件关键词")
    is_show = db.Column(db.Integer, default=1, comment="是否展示: 0. 不展示, 1. 展示")
    create_time =db.Column(db.DateTime, default=datetime.datetime.now, comment="事件创建时间")
    update_time =db.Column(db.DateTime, default=datetime.datetime.now ,onupdate=datetime.datetime.now, comment="事件更新时间")

    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=True, comment="关联的主题ID")
    event_sub = relationship("Subjects", backref='sub_event', foreign_keys=[subject_id])

    # secondary在当前项目版本中，要用table_name，而非ClassName
    # 关于多对多，开心就好
    event_news = db.relationship('NewFlashInformation', secondary='event_to_news', backref = 'news_event')
    event_info = db.relationship('NewInformation', secondary='event_to_info', backref = 'info_event')

# class CoinInfo(db.Model):
#     """币信息"""
#     __tablename__ = "coin_info"
#     id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     code = db.Column(db.String(16),unique=True, default="", comment="币代码")
#     english_name = db.Column(db.String(64), default="", comment="币名称(英文)")
#     chinese_name = db.Column(db.String(64), default="", comment="币名称(中文)")
#     logo_img = db.Column(db.String(256), default="", comment="币LOGO URL")
#     white_paper = db.Column(db.String(1024), default="", comment="白皮书")
#     shelf_exchange_num = db.Column(db.Integer, comment="上架交易所个数")
#     publish_time = db.Column(db.DateTime, comment="发行时间")
#     max_supply = db.Column(db.Integer, comment="发行总量")
#     intro = db.Column(db.String(10240), default="", comment="介绍")

class Subjects(db.Model):
    """主题表"""
    __tablename__ = "subjects"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=True)

class CountryInfo(db.Model):
    """国家和地区信息表"""
    __tablename__ = "country_info"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    code = db.Column(db.String(3), default="", comment="世界各国和地区名称代码")
    english_name = db.Column(db.String(48), default="", comment="国家和地区名称(英文)")
    chinese_name = db.Column(db.String(48), default="", comment="国家和地区名称(中文)")
    logo_img = db.Column(db.String(500), default="", comment="国家和地区旗帜图片URL")

class ExchangeInfo(db.Model):
    __tablename__ = "exchange_info"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(16), default="", comment="交易所名称代码")
    english_name = db.Column(db.String(64), default="", comment="交易所名称(英文)")
    chinese_name = db.Column(db.String(32), default="", comment="交易所名称(中文)")
    logo_img = db.Column(db.String(256), default="", comment="交易所LOGO URL")


class SpidersVisualizatonBase(db.Model):
    """爬虫可视化基础表"""
    __bind_key__ = "spiders_visualization"
    __tablename__ = "spiders_visualization_base"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    target_url = db.Column(db.String)
    req_method = db.Column(db.Integer, default=0)
    req_headers = db.Column(db.String)
    information_type = db.Column(db.Integer)
    req_code = db.Column(db.String)
    fliter_a_tag = db.Column(db.Integer, default=0)
    html_ls_tag = db.Column(db.String)
    req_params = db.Column(db.String)
    img_watermark = db.Column(db.Integer, default=0)
    time_interval = db.Column(db.Integer, default=0)
    is_userful = db.Column(db.Integer, default=0)
    ls_rule_type = db.Column(db.Integer, default=0)
    get_num = db.Column(db.Integer, default=5)
    spider_ch_name = db.Column(db.String)
    spider_en_name = db.Column(db.String)


class SpidersVisualizationRule(db.Model):
    """可视化规则表"""
    __bind_key__ = "spiders_visualization"
    __tablename__ = "spiders_visualization_rule"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    base_id = db.Column(db.Integer)
    column_type = db.Column(db.Integer)
    ch_name = db.Column(db.String(128))
    en_name = db.Column(db.String(128))
    get_data_way = db.Column(db.Integer)
    get_column_rule = db.Column(db.String(128))
    start_for = db.Column(db.Integer)
    analysis_code = db.Column(db.String(128))
    column_rule_type = db.Column(db.Integer)
    find_all = db.Column(db.Integer)
    column_attribute = db.Column(db.Integer)


class SpidersVisualizationDataHandle(db.Model):
    """可视化数据预处理表"""
    __bind_key__ = "spiders_visualization"
    __tablename__ = "spiders_visualization_data_handle"
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer)
    type = db.Column(db.Integer)
    delete_tag = db.Column(db.String, nullable=True)
    replace_tag = db.Column(db.String, nullable=True)
    end_replace_tag = db.Column(db.String, nullable=True)


####################################### F10相关 ###################################

class CoinBaseInfo(db.Model):
    __tablename__ = "coin_base_info"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(4))
    english_name = db.Column(db.String(64))
    chinese_name = db.Column(db.String(64))
    logo_img = db.Column(db.String(256))
    white_paper = db.Column(db.String(256))
    shelf_exchange_num = db.Column(db.Integer, comment="上架交易所个数")
    publish_time = db.Column(db.Date)
    max_supply = db.Column(db.Integer)
    intro = db.Column(db.String(10240), comment="介绍")
    website_url = db.Column(db.String(256), default="")
    forum_urls = db.Column(db.String(512), default="", comment="论坛(多个，可逗号分隔)")
    block_explorer_urls = db.Column(db.String(512), default="", comment="区块链浏览器(多个，可逗号分隔)")
    github_url = db.Column(db.String(256), default="")
    reddit_url = db.Column(db.String(256), default="")
    facebook_url = db.Column(db.String(256), default="")
    twitter_url = db.Column(db.String(256), default="")
    wallet_url = db.Column(db.String(256), default="")
    telegram_url = db.Column(db.String(256), default="")
    steemit_url = db.Column(db.String(256), default="")
    algorithm = db.Column(db.String(32), default="")
    proof_type = db.Column(db.String(32), default="")
    tags = db.Column(db.String(256), default="", comment="标签(多个，可逗号分隔)")
    boards = db.Column(db.String(256), default="", comment="所属板块ID(多个，可逗号分隔)")
    ico_plan = db.Column(db.String(256), default="", comment="代币分配(方案)")
    ico_cost = db.Column(db.String(256), default="", comment="IOC成本")
    ico_capital = db.Column(db.String(256), default="", comment="募集资金")
    ico_time = db.Column(db.String(64), default="", comment="募集时间")
    is_available = db.Column(db.Integer, default=0)
    is_rated = db.Column(db.Integer, default=0)

class CoinGithubData(db.Model):
    __tablename__ = "coin_github_data"
    # 设置联合主键
    __table_args__ = (
        db.PrimaryKeyConstraint("coin_id", "collection_time", name="prikey"),
    )
    coin_id = db.Column(db.Integer, primary_key=True)
    collection_time = db.Column(db.DateTime, comment="采集数据时的时间(可每天一次或多次)", primary_key=True)
    last_update_time = db.Column(db.DateTime, comment="github最后更新时间")
    contributions_num = db.Column(db.Integer, comment="github贡献者数量")
    release_num = db.Column(db.Integer, comment="github版本数")
    commits_num = db.Column(db.Integer, comment="github提交数")
    watch_num = db.Column(db.Integer, comment="github关注者数量")
    star_num = db.Column(db.Integer, comment="github粉丝数")
    fork_num = db.Column(db.Integer, comment="github复制数")

class CoinSocialData(db.Model):
    """币的社交媒体相关数据"""
    __tablename__ = "coin_social_data"
    __table_args__ = (
        db.PrimaryKeyConstraint("coin_id", "collection_time"),
    )
    coin_id = db.Column(db.Integer, primary_key=True)
    collection_time = db.Column(db.DateTime, primary_key=True)
    reddit_subscribers = db.Column(db.Integer)
    twitter_watchers = db.Column(db.Integer)
    facebook_likes = db.Column(db.Integer)

class PersonInfo(db.Model):
    __tablename__ = "person_info"
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    face_img = db.Column(db.String(256))
    intro = db.Column(db.String(5120))

class OrganizationInfo(db.Model):
    __tablename__ = "organization_info"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    intro = db.Column(db.String(5120))

class ObjectRelationTypes(db.Model):
    __tablename__ = "object_relation_types"
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(64), comment="关系类型描述")

class ObjectRelations(db.Model):
    __tablename__ = "object_relations"
    id = db.Column(db.Integer, primary_key=True)
    obj1_id = db.Column(db.Integer)
    obj2_id = db.Column(db.Integer)
    type = db.Column(db.Integer)
    desc = db.Column(db.String(64))
    score = db.Column(db.Float(20,19))

class CoinRoadmap(db.Model):
    __tablename__ = "coin_roadmap"
    __table_args__ = (
        db.PrimaryKeyConstraint("coin_id", "start_time"),
    )
    coin_id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, primary_key=True)
    work_time_desc = db.Column(db.String(128))
    work_item = db.Column(db.String(512))

class CoinHoldingAddressStatis(db.Model):
    """持币地址统计信息"""
    __tablename__ = "coin_holding_address_statis"
    __table_args__ = (
        db.PrimaryKeyConstraint("coin_id", "collection_time"),
    )
    coin_id = db.Column(db.Integer, primary_key=True)
    collection_time = db.Column(db.DateTime, primary_key=True)
    holding_address_num = db.Column(db.Integer)
    top10_holding_coins = db.Column(db.Integer)
    current_total_coins = db.Column(db.Integer)
    holding_concent_degree = db.Column(db.Integer)

# class CoinRatingScore(db.Model):
#     """币的评级评分信息"""
#     coin_id = db.Column(db.Integer, primary_key=True)
#     # ???????????????????????????????????????????????
#
#     pass

class CoinBoardInfo(db.Model):
    """板块类别信息"""
    __tablename__ = "coin_board_info"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    intro = db.Column(db.String(5120))

class CoinCashFlow(db.Model):
    """币的资金流向"""
    __tablename__ = "coin_cash_flow"
    __table_args__ = (
        db.PrimaryKeyConstraint("coin_id", "collection_time"),
    )
    coin_id = db.Column(db.Integer, primary_key=True)
    collection_time = db.Column(db.DateTime, primary_key=True)
    big_inflow = db.Column(db.Float(20,2), comment="大单流入")
    big_outflow = db.Column(db.Float(20,2), comment="大单流出")
    mid_inflow = db.Column(db.Float(20,2), comment="中单流入")
    mid_outflow = db.Column(db.Float(20,2), comment="中单流出")
    lit_inflow = db.Column(db.Float(20,2), comment="小单流入")
    lit_outflow = db.Column(db.Float(20,2), comment="小单流出")

# class FearAndGreedIndex(db.Model):
#     """恐惧贪婪指数"""
#     __tablename__ = "fear_and_greed_index"
#     timestamp = db.Column(db.BigInteger)
#     value = db.Column(db.Float(10,2))


class FootBar(db.Model):
    """资讯底部宣传文"""
    __tablename__ = "foot_bar"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(20480), default="", comment="宣传内容")
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    is_delete = db.Column(db.Integer, default=0, comment="是否删除: 0:未删，1：删掉")


class AccountManage(db.Model):
    """账户管理"""
    __tablename__ = "account_manage"
    id = db.Column(db.Integer, primary_key=True)
    account_name = db.Column(db.String(64), default="")
    account_password = db.Column(db.String(32), default="")
    account_rank = db.Column(db.Integer)
    account_article_num = db.Column(db.Integer)
    account_type = db.Column(db.Integer)
    total_read_num = db.Column(db.Integer)
    total_play_num = db.Column(db.Integer)
    total_subscribe_num = db.Column(db.Integer)
    account_index = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    update_time = db.Column(db.DateTime, onupdate=datetime.datetime.now)