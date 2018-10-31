# encoding=gbk
import requests

# 推送服务
def common_push_server(content):
    data = {}
    if len(content)>200:
        content = content[:150] + "..."
    data["info"] = content
    url = "http://aibicoin.com:5000/api/v1/manage/message/pushinfo"
    resp = requests.post(url, data)
    data['key'] = "4a9b109cbcc2cc2bc4be48fd"
    data['secret'] = "ec19f9ffd621af3388c1959d"
    requests.post(url,data)

    return resp.status_code
