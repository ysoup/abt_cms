import requests, json
from flask import current_app


def common_byj_info():
    # url = current_app.config['REQUEST_URL'] + "/api/v1/manage/project/textinfo?projectno=6"
    url =  current_app.config['REQUEST_URL'] + "/api/v1/manage/project/textinfo?projectno=6"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    else:
        current_app.logger.error("common_byj_info() is not response!!! status_codes is %s"%res.status_code)
        return False

def common_delete_user_byj(id, flag):
    url = current_app.config['REQUEST_URL'] + '/api/v1/manage/project/textinfo/delete'
    data = {'id':id, 'type':'3', 'flag':flag}
    res =requests.post(url, data)
    return res