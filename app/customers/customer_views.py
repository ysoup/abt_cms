import json, datetime
# 导入蓝图
from . import customer
from common.customer_service import *
from flask_login import login_required
from ..utils.Pagination import Pagination
from flask import request, render_template, jsonify, current_app


# 所有客户信息
@customer.route("/customer/customers", methods=['GET', "POST"])
@login_required
def customers():
    if request.method == 'GET':
        try:
            res = json.loads(common_get_customers())
            if res.get("code") != 0:
                current_app.logger.error("customers - res.code != 0", res.get("code"))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")),
                                   request.path, request.args, per_page_count=50)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("customer/customers.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 创建新客户
@customer.route("/customer/createcustomer", methods=['GET', "POST"])
@login_required
def create_customer():
    if request.method == "GET":
        return render_template("customer/create_customer.html")
    elif request.method == "POST":
        try:
            data = {
                "customer_name": request.form.get("customer_name", ""),
                "nickname": request.form.get("nickname", ""),
                "email": request.form.get("email", ""),
                "mobile_no": request.form.get("mobile_no", ""),
                "image_no": request.form.get("image_no"),
                "customer_status": request.form.get("customer_status", ""),
                "customer_type": request.form.get("customer_type", ""),
                "customer_grade": request.form.get("customer_grade", ""),
                "customer_score": request.form.get("customer_score", ""),
                "source_flag": request.form.get("source_flag", ""),
                "source": request.form.get("source", ""),
                "remark": request.form.get("remark", ""),
            }
            res = json.loads(common_create_customer(data))
            if res.get("code") != 0:
                current_app.logger.error("/customer/createcustomer POST - res.code != 0", res.get("code"))
                return jsonify({'failed': '操作失败，请重试'})
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

# 单个客户资产
@customer.route("/customer/asset", methods=['GET', "POST"])
@login_required
def customer_asset_info():
    if request.method == 'GET':
        try:
            customerno = request.args.get("customerno")
            res = json.loads(common_customer_asset(customerno))
            if res.get("code") != 0:
                current_app.logger.error("customer_asset_info - res.code != 0", res.get("code"))
                return render_template("404.html")
            return render_template("customer/customer_asset_info.html", data=res)

        except Exception as e :
            current_app.logger.error(e)
            return render_template("404.html")


# 单个客户信息的查看与修改
@customer.route("/customer/customerinfo", methods=["GET", "POST"])
@login_required
def customer_info():
    if request.method == "GET":
        try:
            customer_no = request.args.get("customer_no")
            res = json.loads(common_get_customer_detail(customer_no))
            if res.get("code") != 0:
                current_app.logger.error("customer_info - res.code != 0", res.get("code"))
                return render_template("404.html")
            return render_template("customer/modify_customer_detail.html", data=res.get('data'))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == "POST":
        try:
            data = {
                "customer_no": request.form.get("customer_no"),
                "customer_name": request.form.get("customer_name"),
                "nickname": request.form.get("nickname"),
                "email": request.form.get("email"),
                "mobile_no": request.form.get("mobile_no"),
                "image_no": request.form.get("image_no"),
                "customer_status": request.form.get("customer_status"),
                "customer_type": request.form.get("customer_type"),
                "customer_grade": request.form.get("customer_grade"),
                "customer_score": request.form.get("customer_score"),
                "source_flag": request.form.get("source_flag"),
                "source": request.form.get("source"),
                "remark": request.form.get("remark")
            }
            res = json.loads(common_modify_customer_detail(request.form.get("customer_no"), data))
            if res.get("code") != 0:
                current_app.logger.error("/customer/customerinfo POST - res.code != 0", res.get("code"))
                return jsonify({'failed': '操作失败，请重试'})
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


import os, sys
from PIL import Image

BASE_PIC = os.path.join(sys.path[0], "app", "static", "pic")
BASE_PIC_URL = '/static/pic'
from ..new_flash.hadoop_service import *
# 获取用户图片
@customer.route('/upload_customer_img', methods=['POST'])
def upload_customer_img():
    if request.method == 'POST':
        try:
            import time
            uu = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            file_obj = request.files.get('file')
            fname, fext = os.path.splitext(file_obj.filename)
            base_pic = BASE_PIC + "/customer_" + uu + fext
            base_pic_url = BASE_PIC_URL + "/customer_" + uu + fext
            img = Image.open(file_obj)
            if len(img.split()) == 4:
                # prevent IOError: cannot write mode RGBA as BMP
                r, g, b, a = img.split()
                img = Image.merge("RGB", (r, g, b))
            img.thumbnail((200, 200), Image.ANTIALIAS)
            img.save(base_pic)
            filename = base_pic_url.replace("/static/pic/", '')
            # 上传hadoop
            new_img_url = upload_images_hdfs(filename, base_pic)
            if not new_img_url:
                return jsonify({'failed': '上传hadoop失败，请重试！'})
            os.remove(base_pic)
            return jsonify({'success': 'ok', "new_img_url": new_img_url})
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'failed': '出错了，请查看日志'})
