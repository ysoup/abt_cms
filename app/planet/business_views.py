from . import planet
import json, datetime
from flask import current_app, request, render_template, jsonify
from ..utils.Pagination import Pagination
from common.planet_service import *


# 商家信息
@planet.route("/planet/business")
def business_info():
    if request.method == 'GET':
        try:
            res = common_get_business()
            if res.get("code") != 0:
                current_app.logger.error("planet_info - res.code != 0", res.get('code'))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path, request.args,
                                   per_page_count=10)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            query_time = res.get("current_time")
            return render_template("planet/business.html", data=data, html=html, query_time=query_time)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
