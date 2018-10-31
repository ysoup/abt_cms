import requests, json
from flask import current_app

# REQUEST_URL = "http://192.168.2.84:5000"


# /api/v1/manage/project/projectno/<projectno> 
def common_viewuser(pro_no):
    try:
        url = current_app.config['REQUEST_URL'] + "/api/v1/manage/project//projectno/" + pro_no
        res = requests.get(url)
        if res.status_code == 200 :
            return res.text
    except Exception as e:
        current_app.logger.error(e)

def common_addparticipation(projectno, invitationcode, number):
    # 生成二级用户
    try:
        url = current_app.config["REQUEST_URL"] + "/api/v1/manage/project/addparticipation"
        data = {"projectno":projectno, "invitationcode":invitationcode, "number":number}
        res = requests.post(url, data)
        return res.text
    except  Exception as e :
        current_app.logger.error(e)

def common_createuser(projectno, number, ceilmember, floormember):
    try:
        url = current_app.config["REQUEST_URL"] + "/api/v1/manage/project/createuser"
        data = {"projectno":projectno, "number":number, "ceilmember":ceilmember, "floormember":floormember}
        res = requests.post(url, data)
        return res.text
    except Exception as e:
        current_app.logger.error(e)