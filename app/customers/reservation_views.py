import json, datetime
# 导入蓝图
from . import customer
from common.customer_service import *
from flask_login import login_required
from ..utils.Pagination import Pagination
from flask import request, render_template, jsonify, current_app

RESERVATION = 8

@customer.route("/customer/reservation", methods=['GET', 'POST'])
def reservation_info():
    if request.method == 'GET':
        try:
            # 目前固定为 "8"
            projectno = str(RESERVATION)
            res = common_get_reservation(projectno)
            if res.get("code") != 0:
                current_app.logger.error("reservation_info() - res.code != 0", res.get("code"))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")),
                                   request.path, request.args, per_page_count=20)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("customer/reservation.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

@customer.route("/customer/reservation_send_sms", methods = ['GET', "POST"])
def reservation_send_sms():
    if request.method == 'POST':
        try:
            projectno = str(RESERVATION)
            res = common_reservation_send_sms(projectno)
            if res.get("code") != 0:
                current_app.logger.error("reservation_info() - res.code != 0", res.get("code"))
                return render_template("404.html")
            return jsonify({"status":"ok", "msg": "已成功安排短信%s条！"%res.get("number")})

        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
