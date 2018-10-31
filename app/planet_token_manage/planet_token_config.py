from . import planet_token
import json, datetime
from flask_login import login_required
from flask import current_app, request, render_template, jsonify
from ..utils.Pagination import Pagination
from common.planet_service import *


@planet_token.route("/gather/config_list")
@login_required
def config_list():
    try:
        res = json.loads(common_get_token_config())
        if res.get('code') != 0:
            current_app.logger.error("/gather/config_list - res.code != 0", res.get('code'))
            return render_template("404.html")
        pager_obj = Pagination(request.args.get("page", 1), len(res.get("info")), request.path, request.args,
                               per_page_count=10)
        data = res.get("info")[pager_obj.start:pager_obj.end]
        html = pager_obj.page_html()
        return render_template("planet_token/config_info.html", data=data, html=html,
                               query_time=res.get("current_time"))

    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")

@planet_token.route("/gather/add_planet_config", methods=["GET", "POST"])
@login_required
def add_planet_config():
    if request.method == 'GET':
            return render_template("planet_token/add_planet_config.html")
    elif request.method == 'POST':
        try:
            issue_time = request.form.get("issue_time", "08:00")
            data = {
                    "token_no": request.form.get("token_no") ,
                    "issue_time": issue_time,
                    "token_num": request.form.get("token_num"),
                    "is_userful": request.form.get("is_userful", 1),
                    }
            res = json.loads(common_add_config(data))
            print(res.get("code"))
            if res.get('code') == 0:
                return jsonify({'success': 'ok'})
            elif res.get("code") == 2:
                return jsonify({"failed":"Token编号未找到，请重新操作。"})
            return jsonify({'failed': '添加失败，请重试'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

@planet_token.route("/gather/modify_planet_config", methods=["GET", "POST"])
@login_required
def modify_planet_config():
    if request.method == 'GET':
        try:
            sn = request.args.get("sn")
            res = json.loads(common_get_detail_config(sn))
            if res.get("code") != 0:
                current_app.logger.error("modify_config - res.code != 0 ", res.get("code"))
                return render_template("404.html")
            return render_template("planet_token/modify_planet_config.html", data=res.get("info"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

    elif request.method == 'POST':
        try:
            sn = request.form.get("sn")
            issue_time = request.form.get("issue_time", "08:00")
            data = {
                    "sn": sn,
                    "token_no": request.form.get("token_no") ,
                    "issue_time": issue_time,
                    "token_num": request.form.get("token_num"),
                    "is_userful": request.form.get("is_userful", 1),
                    }
            res = common_modify_config(data)
            if json.loads(res).get('code') == 0:
                return jsonify({'success': 'ok'})
            return jsonify({'failed': '编辑失败，请重试'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

@planet_token.route("/gather/modify_config_status", methods=["POST"])
@login_required
def modify_config_status():
    if request.method == "POST":
        try:
            is_userful = request.form.get("is_userful")
            sn = request.form.get("sn")
            data = {"sn": sn, "is_userful": is_userful}
            res = common_modify_config_status(data)
            if json.loads(res).get('code') == 0:
                return jsonify({'success': 'ok'})
            return jsonify({'failed': '状态修改，请重试'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")