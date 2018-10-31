import re
from flask import Blueprint, request, session ,render_template, redirect, current_app, url_for
from db import session_conn  # sqlalchemy连接
from flask_admin import BaseView, expose
from flask import g

rbac_blue = Blueprint('rbac_blue', __name__)

@rbac_blue.before_app_request
def process_request():
    current_url = request.path
    VALID_URL = current_app.config['VALID_URL']

    # 1. 白名单验证
    valid_url = VALID_URL
    for each in valid_url:
        if re.match(each, valid_url):
            return None

    # 2. 验证是否已经登录
    permission_dic = session.get('show_per_dic')
    if not permission_dic:
        return redirect(url_for('main.login'))

    # 3. 判断当前访问url与当前登录用户的权限是否匹配，并在request中写入code信息
    flag = False
    for group_id, code_urls in permission_dic.items():
        for url in code_urls['per_url']:
            regex = '^{0}$'.format(url)
            if re.match(regex, url):
                flag = True
                # 用于在页面判断当前用户的权限信息
                request.permission_code_list = code_urls['code']

                code_list = request.permission_code_list
                page_permission = 111
    # 未完待续...
    pass
