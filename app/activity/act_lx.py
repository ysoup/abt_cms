import json

from flask import request, render_template, jsonify, current_app
from flask_login import login_required

from common.act.act_lx import common_user, common_delete_user, common_act_info, common_add_act
# 导入蓝图
from . import act
from ..utils.Pagination import Pagination

PROJECTNO = str(4)

# 拉新活动主页面
@act.route("/act_lx")
@login_required
def act_lx():
    try:
        if request.args.get("stage"):
            res = json.loads(common_user("stage", request.args.get("stage"), PROJECTNO))
        elif request.args.get("telephone"):
            res = json.loads(common_user("telephone", request.args.get("telephone"), PROJECTNO))
        else:
            res = json.loads(common_user("","", PROJECTNO))
        res1 = json.loads(common_act_info(PROJECTNO))
        if res['code'] == 0:
            l = res.get("info")
            l_act = res1.get("data")[0].get("stageinfo")
            pager_obj = Pagination(request.args.get("page", 1), len(l), request.path, request.args, per_page_count=50)
            # pager_obj_act = Pagination(request.args.get("page", 1), len(l_act), request.path, request.args, per_page_count=100)
            data = l[pager_obj.start:pager_obj.end]
            # data_act = l_act[pager_obj_act.start:pager_obj_act.end]
            html = pager_obj.page_html()
            # html_act = pager_obj_act.page_html()
            return render_template("activity/lxhd/act_lx.html", data=data, html=html, data_act=l_act)
        else:
            current_app.logger.error("act_lx.py- res.code!= 0")
            return render_template("404.html")
    except Exception as e :
        current_app.logger.error(e)
        return render_template("404.html")

# 删除用户
@act.route("/delete_user_lx", methods=['GET', 'POST'])
@login_required
def delete_user_lx():
    if request.method == "POST":
        try:
            id = request.form['id']
            stage = request.form["stage"]
            data = common_delete_user(id, stage, PROJECTNO)
            if data.status_code == 201:
                if json.loads(data.text).get('code') == 0:
                    return jsonify({'success': 'ok'})
            return jsonify({'failed': '未删除成功'})
        except Exception as e:
            current_app.logger.error(e)
        return jsonify({'failed': '好像是出了什么问题'})

# 新增当前活动轮数
@act.route("/add_act_lx", methods=["GET", "POST"])
@login_required
def add_act_lx():
    if request.method == 'GET':
        return render_template("activity/lxhd/add_act.html")
    elif request.method == 'POST':
        try:
            if json.loads(common_act_info(PROJECTNO))['code'] == 0:
                data = json.loads(common_act_info(PROJECTNO)).get("data")[0]
                data_info = data.get("stageinfo")
                end_time = request.form.get("end_time")
                per_amount = str(float(request.form.get("per_amount"))/1000)
                stage = len(data_info)+1
                start_time = request.form.get("start_time")
                total_amount = request.form.get("total_amount")
                total_member = request.form.get("total_member")
                info = {'asset_id': 'btc', 'end_time': end_time, 'member': 0, 'per_amount': per_amount, 'stage': str(stage), 'start_time': start_time, 'total_amount': total_amount, 'total_member': total_member}
                data_info.append(info)
                if not data.get("duration"):
                    data['duration'] = ""
                res = common_add_act(data)
                if json.loads(res).get('code') == 0:
                    return jsonify({'success': 'ok'})
            return jsonify({'failed': '添加失败'})
        except Exception as e :
            current_app.logger.error(e)
            return jsonify({'failed': '好像是出了什么问题'})

# 编辑当前活动
@act.route("/modify_act_lx", methods=["GET", "POST"])
@login_required
def modify_act_lx():
    if request.method == 'GET':
        try:
            stage = request.args.get("stage")
            res = json.loads(common_act_info(PROJECTNO))
            if res['code'] == 0:
                l_act = res.get("data")[0].get("stageinfo")
                for item in l_act:
                    if stage == item["stage"]:
                        return render_template("activity/lxhd/modify_act.html", data=item)
                current_app.logger.error("act_lx.py- 97, stage is not found!")
                return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            if json.loads(common_act_info(PROJECTNO))['code'] == 0:
                data = json.loads(common_act_info(PROJECTNO)).get("data")[0]
                data_info = data.get("stageinfo")
                end_time = request.form.get("end_time")
                stage = request.form.get("stage")
                start_time = request.form.get("start_time")
                total_amount = request.form.get("total_amount")
                total_member = request.form.get("total_member")
                for item in data_info:
                    if stage == item["stage"]:
                        item["end_time"] = end_time
                        item["start_time"] = start_time
                        item["total_amount"] = total_amount
                        item["total_member"] = total_member
                if not data.get("duration"):
                    data['duration'] = ""
                res = common_add_act(data)
                if json.loads(res).get('code') == 0:
                    return jsonify({'success': 'ok'})
                return jsonify({'failed': '编辑失败'})
        except Exception as e :
            current_app.logger.error(e)
            return jsonify({'failed': '在POST请求时发生失败。'})