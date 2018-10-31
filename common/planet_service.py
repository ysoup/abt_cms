import requests, json
from flask import current_app


req_url = "http://192.168.2.243:5000"

def common_planet_info():
    """获取星球信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/planet/info"
    # url = req_url + "/api/v1/manage/planet/info"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_planet_info() is not response! StatusCode is %s."%res.status_code)
    return False

def common_planet_detail(planet_no):
    """获取单个星球信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/planet/info/" + planet_no
    # url = req_url + "/api/v1/planet/info/" + planet_no
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_planet_info() is not response! StatusCode is %s."%res.status_code)
    return False

def common_modify_planet(planet_no, data):
    """修改星球信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/planet/info/" + planet_no
    # url = req_url + "/api/v1/planet/info/" + planet_no
    res = requests.post(url, data)
    return res

# 编辑Token信息
def common_planet_token_detail(sn=None, data="", flag=False):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/modify_planet_token?sn=%s' % sn
    # url = req_url + '/api/v1/manage/modify_planet_token?sn=%s' % sn
    if flag :
        res = requests.get(url)
    else:
        res = requests.post(url,data)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_planet_token_detail() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 新增Token
def common_add_planet_token(data):
    url = current_app.config.get("REQUEST_URL") + "/api/v1/manage/add_planet_token"
    # url = req_url + "/api/v1/manage/add_planet_token"
    res = requests.post(url, data)
    if res.status_code == 200:
        return json.loads(res)
    current_app.logger.error("common_add_planet_token() is not correct response! StatusCode is %s" % res.status_code)

def common_add_planet(data):
    """新增星球信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/planet/add_planet"
    # url = req_url + "/api/v1/manage/planet/add_planet"
    res = requests.post(url, data)
    if res.status_code == 200 :
        return res.text
    current_app.logger.error("common_add_planet() is not response! StatusCode is %s."%res.status_code)
    return False

def common_planet_owner():
    """获取星球主信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/planet/owner_info"
    # url = req_url + "/api/v1/manage/planet/owner_info"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_planet_owner() is not response! StatusCode is %s."%res.status_code)
    return False

def common_modify_planet_owner(data=None, flag=False, sn=None):
    """编辑星球主信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/planet/modify_planet_owner?sn=%s" %sn
    # url = req_url + "/api/v1/manage/planet/modify_planet_owner?sn=%s" %sn
    if flag:
        res = requests.get(url)
    else:
        res = requests.post(url, data)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_modify_planet_owner() is not response! StatusCode is %s."%res.status_code)
    return False

def common_add_planet_owner(data):
    """新增星球主"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/planet/add_planet_owner"
    # url = req_url + "/api/v1/manage/planet/add_planet_owner"
    res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_add_planet_owner() is not response! StatusCode is %s."%res.status_code)

def common_planet_token():
    """获取星球币信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/planet/token_info"
    # url = req_url + "/api/v1/manage/planet/token_info"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_planet_token() is not response! StatusCode is %s."%res.status_code)
    return False

def common_delete_planet(planet_no):
    """删除星球"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/planet/info/" + planet_no
    # url = req_url + "/api/v1/planet/info/" + planet_no
    res = requests.patch(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_delete_planet() is failed! StatusCode is %s."%res.status_code)
    return False

def common_gather_rules():
    """星球币规则"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/collect_coin_rules"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_token_rules() is failed! StatusCode is %s."%res.status_code)
    return False

def common_add_rule(data):
    """添加星球币规则"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/add_collect_coin_rules"
    # url = "http://192.168.2.171:5000/api/v1/manage/add_collect_coin_rules"
    res = requests.post(url, data)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_add_rule() is failed! StatusCode is %s."%res.status_code)
    return False

def common_get_detail_rule(sn):
    """单个规则详情"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/modify_collect_coin_rules?sn=" + sn
    # url = "http://192.168.2.171:5000/api/v1/manage/modify_collect_coin_rules?sn=" + sn
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_get_detail_rule() is failed! StatusCode is %s."%res.status_code)
    return False

def common_modify_rule(data):
    """单个规则详情"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/modify_collect_coin_rules"
    # url = "http://192.168.2.171:5000/api/v1/manage/modify_collect_coin_rules"
    res = requests.post(url, data)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_modify_rule() is failed! StatusCode is %s."%res.status_code)
    return False

def common_modify_status(data):
    """修改状态"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/delete_collect_coin_rules"
    # url = "http://192.168.2.243:5000/api/v1/manage/delete_collect_coin_rules"
    res = requests.post(url,data)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_modify_status() is failed! StatusCode is %s."%res.status_code)
    return False

def common_get_customer_gather_list():
    """获取所有用户采币情况"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/gather_list"
    # url = "http://192.168.2.171:5000/api/v1/manage/gather_list"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_get_customer_gather_list() is failed! StatusCode is %s." % res.status_code)
    return False

def common_get_customer_gather_detail(customer_no):
    """获取单个用户采币情况"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/gather_details_list?customer_no=" + customer_no
    # url = "http://192.168.2.171:5000/api/v1/manage/gather_details_list?customer_no=" + customer_no
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_get_customer_gather_detail() is failed! StatusCode is %s." % res.status_code)
    return False

def common_get_token_config():
    """获取每日发送Token信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/planet_token_config"
    # url = "http://192.168.2.171:5000/api/v1/manage/planet_token_config"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_get_token_config() is failed! StatusCode is %s." % res.status_code)
    return False

def common_get_detail_config(sn):
    """获取单个配置详情"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/modify_planet_token_config?sn=" + sn
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_get_detail_config() is failed! StatusCode is %s."%res.status_code)
    return False

def common_modify_config(data):
    """修改单个配置详情"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/modify_planet_token_config"
    # url = "http://192.168.2.171:5000/api/v1/manage/modify_planet_token_config"
    res = requests.post(url, data)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_modify_config() is failed! StatusCode is %s."%res.status_code)
    return False

def common_add_config(data):
    """添加单个配置详情"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/add_planet_token_config"
    # url = "http://192.168.2.171:5000/api/v1/manage/add_planet_token_config"
    res = requests.post(url, data)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_add_config() is is failed! StatusCode is %s." % res.status_code)
    return False

def common_modify_config_status(data):
    """修改状态"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/delete_planet_token_config"
    # url = "http://192.168.2.243:5000/api/v1/manage/delete_collect_coin_rules"
    res = requests.post(url,data)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_modify_config_status() is failed! StatusCode is %s." % res.status_code)
    return False

def common_get_business():
    """获取商家信息"""
    url = current_app.config.get("REQUEST_URL") + "/api/v1/manage/planet/business_info"
    # url2 = req_url + "/api/v1/manage/planet/business_info"
    res = requests.get(url)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_get_business() is not correct response! StatusCode is %s" % res.status_code)
    return False

######################################### 动态相关 ##################################
# 动态信息
def common_news_notification():
    # url = req_url + "/api/v1/manage/planet/news_notification_list"
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/planet/news_notification_list"
    res = requests.get(url)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_news_notification_list() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 创建动态
def common_create_news_notification(data):
    # url = req_url + "/api/v1/manage/planet/create_news_notification"
    url = current_app.config.get("REQUEST_URL") + "/api/v1/manage/planet/create_news_notification"
    res = requests.post(url, data)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_create_news_notification() is not correct response! StatusCode is %s"% res.status_code)
    return False

# 编辑动态
def common_modify_news_notification(data=None, flag=False, sn=None):
    # url = req_url + "/api/v1/manage/planet/modify_news_notification?sn=%s" % sn
    url = current_app.config.get("REQUEST_URL") + "/api/v1/manage/planet/modify_news_notification?sn=%s" % sn
    if flag:
        res = requests.get(url)
    else:
        res = requests.post(url,data=data)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_modify_news_notification() is not correct! StatusCode is %s"% res.status_code)
    return False


# 公告信息
def common_notice_info():
    # url = req_url + "/api/v1/manage/notice/info"
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/notice/info"
    res = requests.get(url)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_notice_info() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 添加新公告
def common_create_notice(data):
    # url = req_url + "/api/v1/manage/notice/create"
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/notice/create"
    res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_create_notice() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 改变公告状态
def common_modify_notice_status(sn):
    # url = req_url + "/api/v1/manage/notice/modify_status"
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/notice/modify_status"
    res = requests.post(url, sn)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_modify_notice_status() is not correct response! StatusCode is %s" % res.status_code)
    return False

PROJECTNO=9
# 邀请码相关
def common_get_invite_codes():
    # url = req_url + "/api/v1/manage/project/invitationcode?projectno=%s" % 9
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/project/invitationcode?projectno=%s" %(PROJECTNO,)
    res = requests.get(url)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_get_invite_codes() is not correct response! StatusCode is %s" % (res.status_code,))
    return False

# 生成邀请码
def common_generate_invitecodes(data):
    url = current_app.config.get("REQUEST_URL") + "/api/v1/manage/project/invitationcode"
    # url = req_url + "/api/v1/manage/project/invitationcode"
    res = requests.post(url, data)
    if res.status_code == 201 :
        return json.loads(res.text)
    current_app.logger.error("common_generate_invitecode() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 编辑邀请码信息
def common_modify_invite_code(data=None, flag=False, id=None):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/modify_invite_code?id=%s' % id
    # url = req_url + '/api/v1/manage/modify_invite_code?id=%s' % id
    if flag:
        res = requests.get(url)
    else:
        res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_modify_invite_code() is not correct response! StatusCode is %s" % res.status_code)
    return False

    pass

# 改变邀请码status
def common_modify_invite_status(data):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/modify_invite_status'
    # url = req_url + '/api/v1/manage/modify_invite_status'
    res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_modify_invite_status() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 改变邀请码status
def common_modify_invite_visibility(data):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/modify_invite_visibility'
    # url = req_url + '/api/v1/manage/modify_invite_visibility'
    res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_modify_invite_visibility() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 推荐星球
def common_set_hot_planet(data):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/set_hot_planet'
    # url = req_url + '/api/v1/manage/planet/set_hot_planet'
    res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_set_hot_planet() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 推荐TokenInfo(保留)
def common_hot_token():
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/hot_tokens'
    # url = req_url + '/api/v1/manage/planet/hot_tokens'
    res = requests.get(url)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_hot_token() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 推荐Businesses
def common_hot_businesses():
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/hot_businesses'
    # url = req_url + '/api/v1/manage/planet/hot_businesses'
    res = requests.get(url)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_hot_businesses() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 推荐Business新增
def common_set_hot_business(data=None, flag=False, token_no=None):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/set_hot_business?token_no=%s' % token_no
    # url = req_url + '/api/v1/manage/planet/set_hot_business?token_no=%s' % token_no
    if flag:
        res = requests.get(url)
    else:
        res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_set_hot_business() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 编辑推荐Business信息
def common_modify_hot_business(token_no=None, data=None, flag=False):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/modify_hot_business?token_no=%s' % token_no
    # url = req_url + '/api/v1/manage/planet/modify_hot_business?token_no=%s' % token_no
    if flag:
        res = requests.get(url)
    else:
        res = requests.post(url, data)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_modify_hot_business() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 改变Business Status
def common_modify_hot_business_status(data):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/modify_hot_business_status'
    # url = req_url + '/api/v1/manage/modify_hot_business_status'
    res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_modify_hot_business_status() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 推荐Token新增（保留）
def common_set_hot_token(data=None, flag=False, token_no=None):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/set_hot_token?token_no=%s' % token_no
    # url = req_url + '/api/v1/manage/planet/set_hot_token?token_no=%s' % token_no
    if flag:
        res = requests.get(url)
    else:
        res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_set_hot_token() is not correct response! StatusCode is %s" % res.status_code)
    return False

# hot planet info
def common_get_hot_planets():
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/hot_planets'
    # url = req_url + '/api/v1/manage/planet/hot_planets'
    res = requests.get(url)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_get_hot_planet() is not correct response! StatusCode is %s" % res.status_code)
    return False

# del hot planet
def common_del_hot_planet(data):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/del_hot_planet'
    # url = req_url + '/api/v1/manage/planet/del_hot_planet'
    res = requests.post(url,data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_del_hot_planet() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 编辑推荐星球信息
def common_get_hot_planet(planet_no=None, data="", flag=False):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/modify_hot_planet?planet_no=%s' % planet_no
    # url = req_url + '/api/v1/manage/planet/modify_hot_planet?planet_no=%s' % planet_no
    if flag :
        res = requests.get(url)
    else:
        res = requests.post(url,data)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_get_hot_planet() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 编辑推荐Token信息
def common_modify_hot_token(token_no=None, data=None, flag=False):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/planet/modify_hot_token?token_no=%s' % token_no
    # url = req_url + '/api/v1/manage/planet/modify_hot_token?token_no=%s' % token_no
    if flag:
        res = requests.get(url)
    else:
        res = requests.post(url, data)
    if res.status_code == 200:
        return json.loads(res.text)
    current_app.logger.error("common_modify_hot_token() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 改变HotToken Status(保留)
def common_modify_hot_token_status(data):
    url = current_app.config.get("REQUEST_URL") + '/api/v1/manage/modify_hot_token_status'
    # url = req_url + '/api/v1/manage/modify_hot_token_status'
    res = requests.post(url, data)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_modify_hot_token_status() is not correct response! StatusCode is %s" % res.status_code)
    return False
