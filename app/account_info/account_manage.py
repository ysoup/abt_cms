# encoding=utf-8
from flask_login import login_required
from flask import request, render_template, jsonify, flash, abort, url_for, redirect, session, Flask, g, current_app
from . import account
from app.models import AccountManage
from cms_server import db, redis_store
import time, copy
from common import push_service
import json, datetime

# utils相关
from ..utils.filter_char import filter_char
from ..utils.sphinxapi3_query_keyword import query_keyword
from ..utils.Pagination import Pagination
ORIGINAL ='ren_gong'
BGMARKET ='aibitou_market'
SELECT_ID ='select_id'


# 快讯列表页
@account.route('/account_manage_list', methods=['GET'])
@login_required
def account_manage_list():
    try:
        page = request.args.get('page', 1, type=int)
        pagination = AccountManage.query.order_by(AccountManage.create_time.desc()).paginate(page, per_page=10,
                                                                                             error_out=False)
        data = pagination.items
        return render_template('account/account_manage_list.html', data=data, pagination=pagination)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")

# # 快讯关键字搜索
# @new_flash.route('/new_search_result', methods=['GET'])
# @login_required
# def new_search_result():
#     try:
#         keyword = request.args.get("keyword")
#         news_id_list = query_keyword("lives_main lives_delta", keyword, current_app.config['SP_HOST'],current_app.config["SP_PORT"])
#         news_obj_list = []
#         for news_id in news_id_list:
#             flash_obj = NewFlashInformation.query.filter(NewFlashInformation.id == news_id).first()
#             news_obj_list.append(flash_obj)
#         news_obj_list.sort(key=lambda flash_obj: flash_obj.update_time)
#         news_obj_list.reverse()
#         pager_obj = Pagination(request.args.get("page", 1), len(news_obj_list), request.path, request.args, per_page_count=5)
#         data = news_obj_list[pager_obj.start:pager_obj.end]
#         html = pager_obj.page_html()
#         return render_template("new_flash/new_search_result.html", data=data, html=html,result_count=len(news_obj_list))
#     except Exception as e:
#         current_app.logger.error(e)
#     return render_template("new_flash/new_search_result.html")
#
# # 编辑快讯
# @new_flash.route("/modify_new_flash", methods=['GET', 'POST'])
# @login_required
# def modify_new_flash():
#     if request.method == "GET":
#         id = request.args.get('id', type=int)
#         row = NewFlashInformation.query.filter(NewFlashInformation.id == id).all()
#         category = NewFlashCategory.query
#         return render_template('new_flash/modify_new_flash.html', data=row, rows=category)
#     elif request.method == "POST":
#         try :
#             title = request.form.get('title')
#             if title == None or title == "":
#                 title = ""
#             info = NewFlashInformation.query.filter_by(id=request.form['id']).first()
#             origin_push = info.is_push
#             info.content = request.form['content']
#             info.category = request.form['category']
#             is_show = request.form['is_show']
#             if not is_show:
#                 is_show = 0
#             info.is_show = is_show
#             info.is_push = request.form['is_push']
#             info.remarks = request.form['remarks']
#             info.highlight_color = request.form['highlight_color']
#             info.update_time = datetime.datetime.now()
#             info.title = title
#             if int(origin_push) == 0  and int(info.is_push) == 1:
#                 try:
#                     content = title
#                     content_text = copy.deepcopy(content)
#                     content_text = filter_char(content_text)
#                     code = push_service.common_push_server(content_text)
#                     if code == 201:
#                         info.is_push = 1
#                 except Exception as e:
#                     current_app.logger.error("new_flash_list.py - 89 push_service.common_push_server is error!", e)
#                     return jsonify({"failed":"推送过程发生问题，请重试"})
#             if info.is_push ==1 or info.is_show == 1:
#                 info.is_show = 1
#                 info.possible_similarity = 0
#             db.session.commit()
#             return jsonify({"success":"ok"})
#         except Exception as e :
#             current_app.logger.error(e)
#             db.session.rollback()
#             return jsonify({'failed': '修改失败'})
#
# # 添加快讯
# @new_flash.route("/add_new_flash", methods=['GET', 'POST'])
# @login_required
# def add_new_flash():
#     if request.method == "GET":
#         category = NewFlashCategory.query.filter_by(is_delete=0)
#         return render_template('new_flash/add_new_flash.html', rows=category)
#     elif request.method == "POST":
#         try:
#             title = request.form.get("title")
#             if title == None or title == "":
#                 title = ""
#             info = NewFlashInformation(content=request.form['content'], category=request.form['category'],highlight_color=request.form['highlight_color'],
#                                        is_show=int(request.form['is_show']),is_push=int(request.form["is_push"]),
#                                        remarks=request.form['remarks'], source_name="ren_gong", content_id=int(time.time()), title=title)
#             db.session.add(info)
#             if info.is_push == 1:
#                 content = title
#                 content_text = copy.deepcopy(content)
#                 content_text = filter_char(content_text)
#                 code = push_service.common_push_server(content_text)
#                 if code == 201:
#                     info.is_push = 1
#                     info.is_show = 1
#             db.session.commit()
#             return jsonify({'success': 'ok'})
#         except Exception as e :
#             current_app.logger.error(e)
#             db.session.rollback()
#             return jsonify({'failed': 'ok'})
#
# # 删除快讯
# @new_flash.route("/delete_new_flash", methods=['GET', 'POST'])
# @login_required
# def delete_new_flash():
#     if request.method == "POST":
#         info = NewFlashInformation.query.filter_by(id=request.form['id']).first()
#         info.is_delete = 1
#         info.is_show = 0
#         db.session.commit()
#         return jsonify({'success': 'ok'})
#
# # 批量删除快讯
# @new_flash.route('/delete_choice_flash', methods=['POST'])
# @login_required
# def delete_choice_flash():
#     if request.method == 'POST':
#         id_list = request.get_data()
#         id_list = json.loads(id_list.decode('utf-8'))
#         for id in id_list:
#             info = NewFlashInformation.query.filter_by(id=int(id)).first()
#             info.is_delete = 1
#             info.is_show = 0
#         db.session.commit()
#         return jsonify({'success': 'ok'})
#
# # 快讯推送
# @new_flash.route("/push_new_flash", methods=['POST'])
# @login_required
# def push_new_flash():
#     if request.method == "POST":
#         id = request.form['id']
#         row = NewFlashInformation.query.filter(NewFlashInformation.id == id).first()
#         if row.is_push != 1:
#             content_text = copy.deepcopy(row.title)
#             content_text = filter_char(content_text)
#             code = push_service.common_push_server(content_text)
#             if code == 201:
#                 row.is_push = 1
#                 row.is_show = 1
#                 row.possible_similarity = 0
#                 db.session.commit()
#                 return jsonify({'success': 'ok'})
#         else:
#             return jsonify({'failed': 'ok'})
#
# # 快讯展示
# @new_flash.route("/show_new_flash", methods=['POST'])
# @login_required
# def show_new_flash():
#     if request.method == "POST":
#         id = request.form['id']
#         row = NewFlashInformation.query.filter(NewFlashInformation.id == id).first()
#         if row.is_show != 1:
#             row.is_show = 1
#             row.possible_similarity = 0
#             db.session.commit()
#             return jsonify({'success': 'ok'})
#         else:
#             return jsonify({'failed': 'ok'})
#
# # 取消快讯展示
# @new_flash.route("/close_new_flash", methods=['POST'])
# @login_required
# def close_new_flash():
#     if request.method == "POST":
#         id = request.form['id']
#         row = NewFlashInformation.query.filter(NewFlashInformation.id == id).first()
#         if row.is_show == 1:
#             row.is_show = 0
#             db.session.commit()
#             return jsonify({'success': 'ok'})
#         else:
#             return jsonify({'failed': 'ok'})
#
# # 定时获取新快讯
# @new_flash.route("/timer_getting_news", methods=['GET'])
# @login_required
# def timer_getting_news():
#     try:
#         since_id = request.args.get("since_id")
#         since_id = since_id if since_id else 0
#         new_obj_count = NewFlashInformation.query.filter(NewFlashInformation.is_delete == 0,NewFlashInformation.id > since_id).count()
#         obj_count = new_obj_count if  new_obj_count else 0
#         return jsonify({"success":"ok", "obj_count": obj_count})
#     except Exception as e:
#         current_app.logger.error(e)
#         return render_template("404.html")
#
# # 初始加载获取id
# @new_flash.route('/get_news_id', methods=['GET'])
# @login_required
# def get_news_id():
#     try:
#         initial_news_id = NewFlashInformation.query.filter_by(is_delete=0).order_by(NewFlashInformation.create_time.desc()).first()
#         return jsonify({'success':'ok', 'initial_news_id':initial_news_id.id})
#     except Exception as e :
#         current_app.logger.error(e)
#
# @new_flash.route("/add_auto_push_time", methods=['POST'])
# @login_required
# # @cache.cached(key_prefix="add_auto_push_time_cache")
# def add_auto_push_time():
#     if request.method == "POST":
#         data = {}
#         data["begin_time"] = request.form['begin_time']
#         data["end_time"] = request.form['end_time']
#         redis_store.set("add_auto_push_time_cache", json.dumps(data))
#         return jsonify({'success': 'ok'})
#
#
# ################################################### 规则相关 ######################################
# # 快讯规则列表
# @new_flash.route("/new_flash_rule", methods=['GET'])
# @login_required
# def new_flash_rule():
#     page = request.args.get('page', 1, type=int)
#     pagination = NewFlashRule.query.filter_by(is_delete=0).order_by(NewFlashRule.id).paginate(page, per_page=50, error_out=False)
#     data = pagination.items
#     return render_template('rule/new_flash_rule.html', data=data, pagination=pagination)
#
# # 编辑快讯规则
# @new_flash.route("/modify_rule", methods=['GET', 'POST'])
# @login_required
# def modify_rule():
#     if request.method == "GET":
#         id = request.args.get('id', type=int)
#         row = NewFlashRule.query.filter(NewFlashRule.id == id, NewFlashRule.is_delete == 0)
#         return render_template('rule/modify_rule.html', data=row)
#     elif request.method == "POST":
#         info = NewFlashRule.query.filter_by(id=request.form['id']).first()
#         rule_name = request.form.get('rule_name')
#         if not rule_name:
#             rule_name = ""
#         info.origin_name = request.form['origin_name']
#         info.rule_name = rule_name
#         info.update_time = datetime.datetime.now()
#         db.session.commit()
#         return jsonify({'success': 'ok'})
#
# # 添加快讯规则
# @new_flash.route("/add_rule", methods=['GET', 'POST'])
# @login_required
# def add_rule():
#     if request.method == "GET":
#         return render_template('rule/add_rule.html')
#     elif request.method == "POST":
#         rule_name = request.form['rule_name']
#         if not rule_name:
#             rule_name = ""
#         info = NewFlashRule(origin_name=request.form['origin_name'], rule_name=rule_name, is_delete=0)
#         db.session.add(info)
#         db.session.commit()
#         return jsonify({'success': 'ok'})
#
# # 删除快讯规则
# @new_flash.route("/delete_rule", methods=['GET', 'POST'])
# @login_required
# def delete_rule():
#     if request.method == "POST":
#         info = NewFlashRule.query.filter_by(id=request.form['id']).first()
#         info.is_delete = 1
#         db.session.commit()
#         return jsonify({'success': 'ok'})
#
#
# ################################################### 类别相关 ######################################
# # 快讯类别
# @new_flash.route('/new_flash_category', methods=['GET', 'POST'])
# @login_required
# def new_flash_category():
#     page = request.args.get('page', 1, type=int)
#     pagination = NewFlashCategory.query.filter_by(is_delete=0).order_by(NewFlashCategory.id).paginate(page, per_page=50, error_out=False)
#     data = pagination.items
#     return render_template('new_flash/new_flash_category.html', data=data, pagination=pagination)
#
# # 编辑快讯类别
# @new_flash.route("/modify_new_category", methods=['GET', 'POST'])
# @login_required
# def modify_new_category():
#     if request.method == "GET":
#         id = request.args.get('id', type=int)
#         row = NewFlashCategory.query.filter(NewFlashCategory.id == id, NewFlashCategory.is_delete == 0)
#         return render_template('new_flash/modify_new_category.html', data=row)
#     elif request.method == "POST":
#         info = NewFlashCategory.query.filter_by(id=request.form['id']).first()
#         info.catname = request.form['catname']
#         info.keyword = request.form['keyword']
#         db.session.commit()
#         return jsonify({'success': 'ok'})
#
# # 添加快讯类别
# @new_flash.route("/add_new_category", methods=['GET', 'POST'])
# @login_required
# def add_new_category():
#     if request.method == "GET":
#         return render_template('new_flash/add_new_category.html')
#     elif request.method == "POST":
#         info = NewFlashCategory(catname=request.form['catname'], keyword=request.form['keyword'], is_delete=0)
#         db.session.add(info)
#         db.session.commit()
#         return jsonify({'success': 'ok'})
#
# # 删除快讯类别
# @new_flash.route("/delete_new_category", methods=['GET', 'POST'])
# @login_required
# def delete_new_category():
#     if request.method == "POST":
#         info = NewFlashCategory.query.filter_by(id=request.form['id']).first()
#         info.is_delete = 1
#         db.session.commit()
#         return jsonify({'success': 'ok'})