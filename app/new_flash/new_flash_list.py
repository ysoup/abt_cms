# encoding=utf-8
from flask_login import login_required
from flask import request, render_template, jsonify, make_response,flash, abort, url_for, redirect, session, Flask, g, current_app
from . import new_flash
from app.models import AccountManage
from cms_server import db, redis_store
import time, copy
from common import push_service
import json, datetime
import os
import xlrd
# utils相关
from ..utils.filter_char import filter_char
from ..utils.sphinxapi3_query_keyword import query_keyword
from ..utils.Pagination import Pagination
from werkzeug.utils import secure_filename


# 快讯列表页
@new_flash.route('/account_manage_list', methods=['GET'])
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


# 新增账户信息
@new_flash.route('/add_account_info', methods=['GET', "POST"])
def add_account_info():
    if request.method == "GET":
        return render_template('account/add_account_info.html')
    elif request.method == "POST":
        try:
            account_name = request.form.get("account_name")
            account_password = request.form.get("account_password")
            account_rank = request.form.get("account_rank")
            account_article_num = request.form.get("account_article_num")

            info = AccountManage(
                account_name=account_name,
                account_password=account_password,
                account_rank=account_rank,
                account_article_num=account_article_num
            )
            db.session.add(info)
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'failed': 'ok'})


# 编辑账户信息
@new_flash.route("/modify_account_info", methods=['GET', 'POST'])
def modify_account_info():
    if request.method == "GET":
        id = request.args.get('id', type=int)
        info = AccountManage.query.filter_by(id=id).first()
        dic = {}
        if info:
            dic["id"] = id
            dic["account_name"] = info.account_name
            dic["account_password"] = info.account_password
            dic["account_rank"] = info.account_rank
            dic["account_article_num"] = info.account_article_num
        return render_template('account/modify_account_manage.html', data=dic)
    elif request.method == "POST":
        try:
            id = request.form.get('id')
            account_name = request.form.get('account_name')
            account_password = request.form.get('account_password')
            account_rank = request.form.get('account_rank')
            account_article_num = request.form.get('account_article_num')
            info = AccountManage.query.filter_by(id=id).first()
            if info:
                info.account_name = account_name
                info.account_password = account_password
                info.account_rank = account_rank
                info.account_article_num = account_article_num
                db.session.add(info)
                db.session.commit()
            return jsonify({"success": "ok"})
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'failed': '修改失败'})


# 文件上传
@new_flash.route('/file_upload', methods=['POST'])
@login_required
def file_upload():
    try:
        file_dict = request.files["file_data"]
        filename = secure_filename(file_dict.filename)
        file_dict.save(os.path.join("./", filename))
        xls_file = xlrd.open_workbook(filename)
        xls_sheet = xls_file.sheets()[0]
        nrows = xls_sheet.nrows
        ncols = xls_sheet.ncols
        for i in range(1, nrows):
            info = []
            for j in range(0, ncols):
                var = xls_sheet.cell(i, j).value
                info.append(var)
            # 数据库持久化
            info = AccountManage(
                account_name=info[0],
                account_password=info[1],
                account_rank=info[2],
                account_article_num=info[3])
            db.session.add(info)
            db.session.commit()
        return jsonify({"success": "ok"})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"success": "failed"})


# 数据统计列表
@new_flash.route('/account_count_list', methods=['GET'])
@login_required
def account_count_list():
    try:
        page = request.args.get('page', 1, type=int)
        pagination = AccountManage.query.order_by(AccountManage.create_time.desc()).paginate(page, per_page=10,
                                                                                             error_out=False)
        data = pagination.items
        return render_template('account/account_count_list.html', data=data, pagination=pagination)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")