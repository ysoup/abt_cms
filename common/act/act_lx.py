import requests, json
from flask import current_app

# PROJECTNO = str(4)

################################################# 用户相关 ##############################################################

# 获取用户信息
def common_user(name,arg,pro_no):
    if arg :
        url = current_app.config["REQUEST_URL"] + "/api/v1/manage/project/rewardinfo?projectno=" + pro_no + "&" + name + "=" + arg
    else:
        url = current_app.config["REQUEST_URL"] + "/api/v1/manage/project/rewardinfo?projectno=" + pro_no
    res = requests.get(url)
    return res.text

# 删除用户
def common_delete_user(id, stage,pro_no):
    url = current_app.config["REQUEST_URL"] + "/api/v1/manage/project/cancelreward"
    data = {"customerid":id, stage:stage, "projectno":int(pro_no)}
    data = requests.post(url,data)
    return data







################################################# 活动相关 ##############################################################

# 获取活动信息
def common_act_info(pro_no):
    url = current_app.config["REQUEST_URL"] + "/api/v1/manage/project/info?projectno=" + pro_no
    res = requests.get(url)
    return res.text

# 添加、编辑新一轮活动
def common_add_act(data):
    try:
        url = current_app.config["REQUEST_URL"] + "/api/v1/manage/project/info"
        res = requests.post(url, data=json.dumps(data))
        return res.text
    except Exception as e :
        current_app.logger.error(e)