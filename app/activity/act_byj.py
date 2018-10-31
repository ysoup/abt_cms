import json
from flask import request, render_template, jsonify, current_app
from flask_login import login_required
# 导入蓝图
from . import act
from common.act.act_byj import common_byj_info,common_delete_user_byj
from ..utils.Pagination import Pagination


# 毕业季活动主页面
@act.route("/act_byj")
@login_required
def act_byj():
    if request.method == 'GET':
        try:
            select_id = request.args.get('select_id')
            sort_pos = request.args.get("sort_pos")
            res = json.loads(common_byj_info())
            data = res['data']
            if select_id:
                data1_list = []
                data2_list = []
                for info in data:
                    if info['delete'] == 0 :
                        data1_list.append(info)
                    else :
                        data2_list.append(info)
                if select_id == '1':
                    data = data1_list
                elif select_id == '2':
                    data = data2_list
            elif sort_pos:
                if sort_pos == str(1):
                        data = sorted(data,  key=lambda e:e['positive'], reverse=True)
                elif sort_pos == str(2):
                        data = sorted(data, key=lambda e:e['positive'], reverse=False)
            else:
                data = res['data']
            pager_obj = Pagination(request.args.get('page', 1), len(data), request.path, request.args, per_page_count=20)
            data_list = data[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            index_url = current_app.config["REQUEST_URL"]
            if res['code'] == 0:
                return render_template("activity/byj/act_byj.html", data=data_list, html=html, index_url=index_url)
        except Exception as e :
            current_app.logger.error(e)

# 删除/恢复用户
@act.route("/delete_user_byj", methods=['POST'])
@login_required
def delete_user_byj():
    try:
        id = request.form.get("id")
        flag = request.form.get("flag")
        res = common_delete_user_byj(id, flag)
        if res.status_code == 201:
            if json.loads(res.text).get('code') == 0:
                return jsonify({'success': 'ok'})
        return jsonify({'failed': '操作失败，请重试'})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'failed': "操作失败，请重试"})

# # 批量操作用户
# @act.route("/delete_user_byj_list", methods=['POST'])
# @login_required
# def delete_user_byj_list():
#     try:
#         if request.method == 'POST':
#             byj_id_list = json.loads(request.get_data())
#             print("byj_id_list===", byj_id_list, type(byj_id_list))
#
#         # id_list = request.get_data()
#         # id_list = json.loads(id_list.decode('utf-8'))
#             for id in byj_id_list:
#                 common_delete_user_byj(id, flag=1)
#             return jsonify({'success': 'ok'})
#     except Exception as e:
#         current_app.logger.error(e)
#         return jsonify({'failed':"ok"})

    # try:
    #     id = request.form.get("id")
    #     res = common_delete_user_sjb(id)
    #     if res.status_code == 201:
    #         if json.loads(res.text).get('code') == 0:
    #             return jsonify({'success': 'ok'})
    #     return jsonify({'failed': '未删除成功'})
    #
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify({'failed': '好像是出了什么问题'})