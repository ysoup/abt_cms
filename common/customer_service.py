import requests, json
from flask import current_app


req_url = "http://192.168.2.243:5000"


def common_get_customers():
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/user/info"
    # url = req_url + "/api/v1/manage/user/info"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error(
        "common_get_customers() is not correct response! StatusCode is %s" % res.status_code)
    return False

def common_get_customer_detail(customer_no):
    """获取单个客户信息"""
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/user/detailinfo/" + customer_no
    # url = req_url + "/api/v1/manage/user/detailinfo/" + customer_no
    res = requests.get(url)
    if res.status_code == 200 :
        return res.text
    current_app.logger.error(
        "common_get_customer_detail() is not correct response! StatusCode is %s" % res.status_code)
    return False

def common_modify_customer_detail(customer_no, data):
    # url = req_url + "/api/v1/manage/user/detailinfo/" + customer_no
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/user/detailinfo/" + customer_no
    res = requests.post(url, data)
    if res.status_code == 200:
        return res.text
    current_app.logger.error(
        "common_modify_customer_detail() is not correct response! StatusCode is %s" % res.status_code)
    return False

def common_create_customer(data):
    # url = req_url + "/api/v1/manage/user/createcustomer"
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/user/createcustomer"
    res = requests.post(url, data)
    if res.status_code == 200:
        return res.text
    current_app.logger.error(
        "common_create_customer() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 客户资产
def common_customer_asset(customer_no):
    # url = req_url + "/api/v1/manage/user/property?customerno=" + customer_no
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/user/property?customerno=" + customer_no
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    current_app.logger.error("common_customer_asset() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 预约信息
def common_get_reservation(projectno):
    # url = req_url + "/api/v1/manage/project/reservation?projectno=" + projectno
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/project/reservation?projectno=" + projectno
    res = requests.get(url)
    if res.status_code == 200 :
        return json.loads(res.text)
    current_app.logger.error("common_get_reservation() is not correct response! StatusCode is %s" % res.status_code)
    return False

# 预约信息
def common_reservation_send_sms(projectno):
    # url = req_url + "/api/v1/manage/project/notification/" + projectno
    url = current_app.config['REQUEST_URL'] + "/api/v1/manage/project/notification/" + projectno
    res = requests.post(url)
    if res.status_code == 201 :
        return json.loads(res.text)
    current_app.logger.error("common_reservation_send_sms() is not correct response! StatusCode is %s" % res.status_code)
    return False