# encoding=utf-8
from flask_login import login_required
from flask import request, render_template, jsonify, make_response,flash, abort, url_for, redirect, session, Flask, g, current_app
from . import new_flash
from app.models import AccountManage, ArticleManage, ArticleUploadManage
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
import docx
import mammoth
import mammoth.transforms
import os
from docx import Document
import zipfile
import requests

styleMap = """

p[style-name='Title'] => h1.hide

p[style-name='Subhead 1'] => h3

p[style-name='List Bullet'] => ul.first > li:fresh

p[style-name='List Bullet 2'] => ul.second > li:fresh

p[style-name='Hyperlink']=>a.link

"""
guidUrl = "https://my.phrplus.com/REST/guid"

imgPath = "/data/imgs"


# 账户列表页
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
            account_type = request.form.get("account_type")
            total_read_num = request.form.get("total_read_num")
            total_play_num = request.form.get("total_play_num")
            total_subscribe_num = request.form.get("total_subscribe_num")
            account_index = request.form.get("account_index")
            account_article_num = request.form.get("account_article_num")

            info = AccountManage(
                account_name=account_name,
                account_password=account_password,
                account_rank=account_rank,
                account_article_num=account_article_num,
                account_type=account_type,
                total_read_num=total_read_num,
                total_play_num=total_play_num,
                total_subscribe_num=total_subscribe_num,
                account_index=account_index
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
            dic["account_type"] = info.account_type
            dic["total_read_num"] = info.total_read_num
            dic["total_play_num"] = info.total_play_num
            dic["total_subscribe_num"] = info.total_subscribe_num
            dic["account_index"] = info.account_index
            dic["account_article_num"] = info.account_article_num
        return render_template('account/modify_account_manage.html', data=dic)
    elif request.method == "POST":
        try:
            id = request.form.get('id')
            account_name = request.form.get('account_name')
            account_password = request.form.get('account_password')
            account_rank = request.form.get('account_rank')
            account_article_num = request.form.get('account_article_num')
            account_type = request.form.get('account_type')
            total_read_num = request.form.get('total_read_num')
            total_play_num = request.form.get('total_play_num')
            total_subscribe_num = request.form.get('total_subscribe_num')
            account_index = request.form.get('account_index')
            info = AccountManage.query.filter_by(id=id).first()
            if info:
                info.account_name = account_name
                info.account_password = account_password
                info.account_rank = account_rank
                info.account_article_num = account_article_num
                info.account_type = account_type
                info.total_read_num = total_read_num
                info.total_play_num = total_play_num
                info.total_subscribe_num = total_subscribe_num
                info.account_index = account_index
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


# 文章列表
@new_flash.route('/article_list', methods=['GET'])
@login_required
def article_list():
    try:
        page = request.args.get('page', 1, type=int)
        pagination = ArticleManage.query.order_by(ArticleManage.create_time.desc()).paginate(page, per_page=10,
                                                                                             error_out=False)
        data = pagination.items
        return render_template('article/article_list.html', data=data, pagination=pagination)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")


# 文章上传
@new_flash.route('/article_file_upload', methods=['POST'])
@login_required
def article_file_upload():
    try:
        file_dict = request.files["file_data"]
        account_type = request.form["account_type"]
        filename = secure_filename(file_dict.filename)
        file_dict.save(os.path.join("./", filename))

        imgNameArr = extractImage(filename)

        article = parseFile(filename)

        fileName = os.path.basename(filename)

        contentArr = article["Content"].split("<img")

        for idx, section in enumerate(contentArr):

            for info in imgNameArr:
                if idx is info["index"]:
                    contentArr[idx] = section + "<img alt='" + info["fileName"] + "' data-fileName='" + info[
                        "fileName"] + "'"
        article["Content"] = ''.join(contentArr)

        # 数据库持久化
        info = ArticleManage(
            article_title=article["Title"],
            article_cover="",
            article_content=article["Content"],
            article_type=account_type,
            is_send=0
        )
        db.session.add(info)
        db.session.commit()
        return jsonify({"success": "ok"})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"success": "failed"})


def extractImage(f):
    ziped = zipfile.ZipFile(f)
    allFiles = ziped.namelist()
    imgs = filter(lambda x: x.startswith('word/media/'), allFiles)
    imgNameArr = []
    for img in imgs:
        res = requests.post(guidUrl)
        if res.status_code is 200:
            guid = res.text
            data = ziped.read(img, bytes(imgPath, encoding="utf-8"))
            idxStr = os.path.basename(img).split(".")[0][-1:]
            imgDict = {}
            imgDict["index"] = int(idxStr)-1
            imgDict["fileName"] = guid+".jpg"
            imgNameArr.append(imgDict)
            targetPath = os.path.join(imgPath, guid+".jpg")
            target = open(targetPath, "wb")
            target.write(data)
            target.close()
    ziped.close()

    return imgNameArr


def parseFile(f):
    document = Document(f)
    article = {"Title": document.paragraphs[0].text, "Content":""}
    with open(f, "rb") as docFile:
        html = mammoth.convert_to_html(docFile, style_map=styleMap,
                                       convert_image=mammoth.images.img_element(convert_image))
    if not article["Title"]:
        for para in document.paragraphs:
            if para.style.name == 'Title':
                if para.text:
                    article["Title"] = para.text

    article["Content"] = html.value
    return article


def convert_image(image):
    return {"src": ""}


# 新增文章信息
@new_flash.route('/add_article_info', methods=['GET', "POST"])
def add_article_info():
    if request.method == "GET":
        return render_template('article/add_article_info.html')
    elif request.method == "POST":
        try:
            article_content = request.form.get("article_content")
            article_title = request.form.get("article_title")
            article_type = request.form.get("article_type")

            info = ArticleManage(
                article_content=article_content,
                article_title=article_title,
                article_type=article_type,
                is_send=0
            )
            db.session.add(info)
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'failed': 'ok'})


# 编辑文章信息
@new_flash.route("/modify_article_info", methods=['GET', 'POST'])
def modify_article_info():
    if request.method == "GET":
        id = request.args.get('id', type=int)
        info = ArticleManage.query.filter_by(id=id).first()
        dic = {}
        if info:
            dic["id"] = id
            dic["article_title"] = info.article_title
            dic["article_content"] = info.article_content
            dic["article_type"] = info.article_type
        return render_template('article/modify_article_manage.html', data=dic)
    elif request.method == "POST":
        try:
            id = request.form.get('id')
            article_title = request.form.get('article_title')
            article_content = request.form.get('article_content')
            article_type = request.form.get('article_type')
            info = ArticleManage.query.filter_by(id=id).first()
            if info:
                info.article_title = article_title
                info.article_content = article_content
                info.article_type = article_type
                db.session.add(info)
                db.session.commit()
            return jsonify({"success": "ok"})
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'failed': '修改失败'})


# 文章上传设置列表
@new_flash.route('/article_upload_set', methods=['GET'])
@login_required                                                                                                 
def article_upload_set():
    try:
        page = request.args.get('page', 1, type=int)
        pagination = ArticleUploadManage.query.order_by(ArticleUploadManage.create_time.desc()).paginate(page,
                                                                                                         per_page=10,
                                                                                                         error_out=False)
        data = pagination.items
        return render_template('article/article_set_list.html', data=data, pagination=pagination)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")


# 新增文章上传设置
@new_flash.route('/add_article_upload_set', methods=['GET', "POST"])
def add_article_upload_set():
    if request.method == "GET":
        info = AccountManage.query.order_by(AccountManage.create_time.desc())
        account_ls = []
        for x in info:
            dic = {}
            dic["id"] = x.id
            dic["account_name"] = x.account_name
            account_ls.append(dic)
        return render_template('article/add_article_upload_set.html', data=account_ls)
    elif request.method == "POST":
        try:
            account_name = request.form.get("account_name")
            article_type = request.form.get("article_type")
            send_type = request.form.get("send_type")

            info = ArticleUploadManage(
                account_name=account_name,
                article_type=article_type,
                send_type=send_type
            )
            db.session.add(info)
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'failed': 'ok'})


# 编辑文章信息
@new_flash.route("/modify_article_upload_set", methods=['GET', 'POST'])
def modify_article_upload_set():
    if request.method == "GET":
        id = request.args.get('id', type=int)
        info = ArticleManage.query.filter_by(id=id).first()
        dic = {}
        if info:
            dic["id"] = id
            dic["article_title"] = info.article_title
            dic["article_content"] = info.article_content
            dic["article_type"] = info.article_type
        return render_template('article/modify_article_upload_set.html', data=dic)
    elif request.method == "POST":
        try:
            id = request.form.get('id')
            article_title = request.form.get('article_title')
            article_content = request.form.get('article_content')
            article_type = request.form.get('article_type')
            info = ArticleManage.query.filter_by(id=id).first()
            if info:
                info.article_title = article_title
                info.article_content = article_content
                info.article_type = article_type
                db.session.add(info)
                db.session.commit()
            return jsonify({"success": "ok"})
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'failed': '修改失败'})
