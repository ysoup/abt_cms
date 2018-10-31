# 导入蓝图
from . import version

import datetime, os, sys
from flask import request, jsonify, render_template
from ..utils.Pagination import Pagination
from common.version_service import *


BASE_FILE = os.path.join(sys.path[0], "app", "static", "app_version", "android")
BASE_FILE_URL = '/static/app_version/android/'
APP_NAME = "aibiPlanet.apk"

# 上传文件保存到服务器
@version.route("/upload_file", methods=['POST'])
def upload_file():
    if request.method == 'POST':
        try:
            file_obj = request.files.get('file')
            base_file = BASE_FILE + "/" + APP_NAME
            # version_file_url = BASE_FILE + "/" + file_obj.filename
            # 前端相对路径用
            base_file_url = BASE_FILE_URL + APP_NAME
            # 删除APK文件
            if os.path.exists(base_file):
                os.remove(base_file)
            with open(base_file, 'wb') as f:
                for i in file_obj:
                    f.write(i)
            return jsonify({'success':'ok', 'file_url':base_file, "base_file_url": base_file_url})
        except Exception as e:
            current_app.logger.error(e)
        return jsonify({'failed': 'ok'})

# 获取版本信息
@version.route("/sys_versions", methods=['GET', "POST"])
def sys_versions():
    if request.method == 'GET':
        try:
            res = common_sys_versions()
            if res.get("code") != 0:
                current_app.logger.error("sys_versions - res.code != 0", res.get('code'))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path, request.args,
                                   per_page_count=10)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("sys_version/sys_versions.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

# 创建版本信息
@version.route("/create_sys_version", methods=['GET', "POST"])
def create_sys_version():
    if request.method == 'GET':
        return render_template("sys_version/create_sys_version.html")
    elif request.method == 'POST':
        try:
            data = request.form.to_dict()
            dl = data.get("download_link").strip()
            ios_url = data.get("ios_url").strip()
            if dl:
                data['download_link'] = dl
            else:
                data['download_link'] = ios_url

            res = common_create_version(data=data)
            if res.get("code") == 0:
                return jsonify({"status": 'success', "msg": res.get('info')})
            return jsonify({"msg": res.get("info")})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

# 编辑版本信息
@version.route("/modify_sys_version", methods=['GET', "POST"])
def modify_sys_version():
    if request.method == 'GET':
        try:
            sn = request.args.get("sn")
            res = common_modify_version(sn=sn, flag=True)
            print(res)
            return render_template("sys_version/modify_sys_version.html", data=res.get("data"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            data = request.form.to_dict()
            dl = data.get("download_link").strip()
            ios_url = data.get("ios_url").strip()
            if dl:
                data['download_link'] = dl
            else:
                data['download_link'] = ios_url
            res = common_modify_version(data=data)
            if res.get("code") == 0:
                return jsonify({"status": 'success', "msg": res.get('info')})
            return jsonify({"msg": res.get("info")})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
