import requests, json
from flask import current_app


req_url = "http://192.168.2.243:5000"
headers = {
    'Connection': 'close',
}

# 获取版本信息
def common_sys_versions():
    # url = req_url + "/api/v1/manage/sys_versions"
    url = current_app.config.get("REQUEST_URL") + "/api/v1/manage/sys_versions"
    res = requests.get(url, headers=headers)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_sys_versions() is not correct response! StatusCode is %s"% res.status_code)
    return False

# 编辑版本信息
def common_modify_version(data=None, flag=False, sn=None):
    # url = req_url + "/api/v1/manage/modify_sys_version?sn=%s" % sn
    url = current_app.config.get("REQUEST_URL") + "/api/v1/manage/modify_sys_version?sn=%s" % sn
    if flag:
        res = requests.get(url, headers=headers)
    else:
        res = requests.post(url, data=data, headers=headers)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_modify_version() is not correct! StatusCode is %s" % res.status_code)
    return False

# 创建版本信息
def common_create_version(data=None):
    # url = req_url + "/api/v1/manage/create_sys_version"
    url = current_app.config.get("REQUEST_URL") + "/api/v1/manage/create_sys_version"
    res = requests.post(url, data=data, headers=headers)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_create_version() is not correct! StatusCode is %s" % res.status_code)
    return False
