from . import planet_token
import json, datetime
from flask import current_app, request, render_template, jsonify
from ..utils.Pagination import Pagination
from common.planet_service import *

@planet_token.route("/gather/rules")
def get_token_rules():
    if request.method == 'GET':
        try:
            res = json.loads(common_gather_rules())
            if res.get('code') != 0:
                current_app.logger.error("get_token_rules - res.code != 0", res.get('code'))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("info")), request.path, request.args,
                                   per_page_count=10)
            data = res.get("info")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet_token/rules_info.html", data=data, html=html, query_time=res.get("current_time"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

@planet_token.route("/gather/add_rule", methods=["GET", "POST"])
def add_rule():
    if request.method == 'GET':
        return render_template("planet_token/add_gather_rule.html")
    elif request.method == 'POST':
        try:
            rule_type = request.form.get("rule_type") if request.form.get("rule_type")!= "" else 1
            data = {"rule_type": rule_type,
                    "token_no": request.form.get("token_no") ,
                    "allocation_time": request.form.get("allocation_time", "08:00"),
                    "expired_time": request.form.get("expired_time", "5"), # 过期时间，如果不填，默认5分钟
                    "time_segments": request.form.get("time_segments", "08:00,10:00,12:00"),
                    "perpage_amount": request.form.get("perpage_amount"),
                    "max_page": request.form.get("max_page"),
                    "remark": request.form.get("remark", ""),
                    "status": request.form.get("status", 0),
                    }
            res = common_add_rule(data)
            if json.loads(res).get('code') == 0:
                return jsonify({'success': 'ok'})
            return jsonify({'failed': '添加失败，请重试'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


@planet_token.route("/gather/modify_rule", methods=["GET", "POST"])
def modify_rule():
    if request.method == 'GET':
        try:
            sn = request.args.get("sn")
            res = json.loads(common_get_detail_rule(sn))
            if res.get("code") != 0:
                current_app.logger.error("planet_detail - res.code != 0 ", res.get("code"))
                return render_template("404.html")
            return render_template("planet_token/modify_gather_rule.html", data=res.get("info"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

    elif request.method == 'POST':
        try:
            rule_type = request.form.get("rule_type") if request.form.get("rule_type")!= "" else 1
            sn = request.form.get("sn")
            data = {
                    "sn": sn,
                    "rule_type": rule_type,
                    "token_no": request.form.get("token_no") ,
                    "allocation_time": request.form.get("allocation_time", "08:00"),
                    "expired_time": request.form.get("expired_time", "5"), # 过期时间，如果不填，默认5分钟
                    "time_segments": request.form.get("time_segments", "08:00,10:00,12:00"),
                    "perpage_amount": request.form.get("perpage_amount"),
                    "max_page": request.form.get("max_page"),
                    "remark": request.form.get("remark", ""),
                    "status": request.form.get("status", 0),
                    }
            res = common_modify_rule(data)
            if json.loads(res).get('code') == 0:
                return jsonify({'success': 'ok'})
            return jsonify({'failed': '编辑失败，请重试'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

@planet_token.route("/gather/modify_rule_status", methods=["POST"])
def modify_rule_status():
    if request.method == 'POST':
        try:
            status = request.form.get("status")
            sn = request.form.get("sn")
            data = {"sn":sn, "status": status}
            res = common_modify_status(data)
            if json.loads(res).get('code') == 0:
                return jsonify({'success': 'ok'})
            return jsonify({'failed': '状态修改失败，请重试'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")