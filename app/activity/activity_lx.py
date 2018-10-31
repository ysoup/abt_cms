import json
from flask import request, render_template, jsonify, current_app
from flask_login import login_required
# 导入蓝图
from . import act
from ..utils.Pagination import Pagination
from common.act.activity_lx import common_viewuser, common_addparticipation, common_createuser

PROJECT_NO = "7"
@act.route("/activity/activity_lx")
@login_required
def activity_lx():
    if request.method == 'GET':
        res = json.loads(common_viewuser(PROJECT_NO))
        try:
            if res.get("code") == 0:
                select_id = request.args.get('select_id', type=int)
                data1_list = []
                data2_list = []
                for re in res.get("detail"):
                    if re.get("flag") == 0 :
                        data1_list.append(re)
                    elif re.get("flag") == 1:
                        data2_list.append(re)

                if select_id == 1:
                    # 真实用户
                    data_list = data2_list
                elif select_id == 2:
                    # 虚拟用户
                    data_list = data1_list
                else:
                    data_list = res.get("detail")
                pager_obj = Pagination(request.args.get("page", 1), len(data_list), request.path, request.args, per_page_count=30)
                data = data_list[pager_obj.start:pager_obj.end]
                html = pager_obj.page_html()
                return render_template("activity/activity_lx/act_lx.html", data = data, html = html)
            current_app.logger.error("/activity/activity_lx - res.code != 0", res.get('code'))
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

# 添加一级用户
@act.route("/activity/add_lx_person", methods=['GET', 'POST'])
@login_required
def add_lx_person():
    if request.method == 'GET':
        return render_template("activity/activity_lx/add_lx_person.html")
    elif request.method == 'POST':
        try:
            person_num = request.form.get("person_num")
            max_hashrate = request.form.get("max_hashrate")
            min_hashrate = request.form.get("min_hashrate")
            res = json.loads(common_createuser(PROJECT_NO, person_num, max_hashrate, min_hashrate))
            print(res)
            if res.get("code") == 0:
                return jsonify({"status":"ok", "msg":"用户添加成功"})
            return jsonify({"status":"failed", "msg":"用户添加失败"})
        except Exception as e :
            current_app.logger.error(e)

# 生成算力(根据邀请码，生成二级用户)
@act.route("/activity/add_participation", methods=['GET', "POST"])
@login_required
def add_participation():
    if request.method == "GET":
        code = request.args.get("code")
        if code:
            return render_template("activity/activity_lx/add_participation.html", code=code)
    if request.method == "POST":
        try:
            number = request.form.get("hashrate")
            code = request.form.get("code")
            res = json.loads(common_addparticipation(PROJECT_NO, code, number))
            if res.get("code") == 0 :
                return jsonify({"status":"ok", 'msg':"算力添加成功"})
            return jsonify({"status":'failed', "msg":"算力添加失败"})
        except Exception as e :
            current_app.logger.error(e)