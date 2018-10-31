from . import planet_token
import json, datetime
from flask import current_app, request, render_template, jsonify
from flask_login import login_required
from ..utils.Pagination import Pagination
from common.planet_service import *


@planet_token.route("/gather/customer_gather", methods=['GET', "POST"])
@login_required
def get_customer_gather():
    if request.method == 'GET':
        try:
            res = json.loads(common_get_customer_gather_list())
            if res.get('code') != 0:
                current_app.logger.error("customer_gather - res.code != 0", res.get('code'))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("info")), request.path, request.args,
                                   per_page_count=10)
            data = res.get("info")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet_token/customer_gather_list.html", data=data, html=html,
                                   query_time=res.get("current_time"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


@planet_token.route("/gather/customer_gather_detail", methods=['GET', "POST"])
@login_required
def customer_gather_detail():
    if request.method == 'GET':
        try:
            customer_no = request.args.get("customer_no")
            res = json.loads(common_get_customer_gather_detail(customer_no))
            if res.get('code') != 0:
                current_app.logger.error("customer_gather_detail - res.code != 0", res.get('code'))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("info")), request.path, request.args,
                                   per_page_count=20)
            data = res.get("info")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet_token/customer_gather_detail.html", data=data, html=html,
                                   query_time=res.get("current_time"), customer_name=res.get("customer_name"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
