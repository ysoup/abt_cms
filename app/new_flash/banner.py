from flask_login import login_required
from flask import request, render_template, jsonify, flash, abort, url_for, redirect, session, Flask, g, current_app
from . import new_flash
from app.models import Banner
from cms_server import db, redis_store
import time
import json
from app.new_flash.hadoop_service import upload_images_hdfs
import os, datetime
import sys

SELECT_ID ='select_id'
BASE_PIC = os.path.join(sys.path[0],"app","static", "pic")
BASE_PIC_URL = '/static/pic'


# banner列表页
@new_flash.route("/banner_list", methods=["GET"])
@login_required
def banner_list():
    page = request.args.get('page', 1, type=int)
    if request.args.get(SELECT_ID) != None:
        val = int(request.args.get(SELECT_ID))
        if val == 0 :
            pagination = Banner.query.order_by(Banner.putaway_time.desc()).paginate(page, per_page=5, error_out=False)
        elif val == 1:
            pagination = Banner.query.filter_by(is_show=1).order_by(Banner.putaway_time.desc()).paginate(page, per_page=5, error_out=False)
        elif val == 2:
            pagination = Banner.query.filter_by(is_show=0).order_by(Banner.putaway_time.desc()).paginate(page, per_page=5, error_out=False)
        else:
            return render_template('404.html')
    else:
        val = 0
        pagination = Banner.query.order_by(Banner.putaway_time.desc()).paginate(page, per_page=5, error_out=False)
    data = pagination.items
    g.select_id = val
    # for item in data:
    #     if item.banner_img.startswith('/aibicloud'):
    #         item.banner_img = item.banner_img
    return render_template('new_flash/banner.html', data=data, pagination=pagination)

# 下架单条banner
@new_flash.route("/delete_banner", methods=["POST"])
@login_required
def delete_banner():
    if request.method == 'POST':
        banner = Banner.query.filter_by(id=request.form['id']).first()
        banner.is_show = 0
        db.session.commit()
        return jsonify({'success':'ok'})

# 下架多条banner
@new_flash.route("/delete_choice_banner", methods=["GET","POST"])
@login_required
def delete_choice_banner():
    if request.method == 'POST':
        try:
            id_list = request.get_data()
            id_list = json.loads(id_list.decode('utf-8'))
            for id in id_list:
                info = Banner.query.filter_by(id=int(id)).first()
                info.is_show = 0
            db.session.commit()
            return jsonify({'success':'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify({'failed': 'ok'})

# 编辑banner
@new_flash.route("/modify_banner", methods=['GET', 'POST'])
@login_required
def modify_banner():
    if request.method == 'GET':
        id = request.args.get('id', type=int)
        row = Banner.query.filter_by(id=id, is_delete=0).first()
        # if row.banner_img.startswith('/aibicloud'):
        #     row.banner_img = row.banner_img
        return render_template('new_flash/modify_banner.html', data=row)
    elif request.method == 'POST':
        try:
            id = request.form.get('id')
            img_obj = request.files.get('img')
            img_url = request.form.get('img_url')
            banner_img = request.form.get('banner_img')
            base_pic_url = request.form.get('base_pic_url')
            desc = request.form.get('desc')
            is_show = request.form.get("is_show")
            # img_url = \PycharmProjects\abt_cms\app\static\pic/banner_9.jpg
            # base_pic_url = /static/pic/banner_9.jpg
            if  banner_img and (img_obj is None):
                banner_obj = Banner.query.filter_by(id=id).first()
                if banner_obj:
                    banner_obj.banner_img = banner_img
                    banner_obj.banner_desc = desc
                    banner_obj.is_show = is_show
                    if int(is_show) == 1:
                        banner_obj.putaway_time = datetime.datetime.now()
                    db.session.commit()
                    return jsonify({"success": 'ok'})
            else:
                filename = base_pic_url.replace("/static/pic/", '')
                new_img_url = upload_images_hdfs(filename, img_url)
                if not new_img_url:
                    return jsonify({'failed':'获取hadoop图片失败，请重试！'})
                banner_obj = Banner.query.filter_by(id=id).first()
                if banner_obj:
                    banner_obj.banner_desc = desc
                    banner_obj.banner_img = new_img_url
                    banner_obj.is_show = is_show
                    if int(is_show) == 1:
                        banner_obj.putaway_time = datetime.datetime.now()
                    db.session.commit()
                    os.remove(img_url)
                    return jsonify({"success": 'ok'})
        except Exception as e  :
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify({'failed':'操作失败，请重试！'})

# 新增banner
@new_flash.route("/add_banner", methods=["GET", "POST"])
@login_required
def add_banner():
    if request.method == 'GET':
        return render_template('new_flash/add_banner.html')
    elif request.method == 'POST':
        try:
            img_obj = request.files.get('img')
            img_url = request.form.get('img_url')
            base_pic_url = request.form.get('base_pic_url')
            desc = request.form.get('desc')
            is_show = request.form.get("is_show")
            putaway_time = datetime.datetime.now()
            if not img_obj and base_pic_url:
                if int(is_show) == 1:
                    banner = Banner(banner_desc=desc, is_show=is_show, putaway_time=putaway_time)
                else:
                    banner = Banner(banner_desc=desc, is_show=is_show)
                db.session.add(banner)
                db.session.commit()
                return jsonify({"success": 'ok'})
            else:
                filename = base_pic_url.replace("/static/pic/", '')
                new_img_url = upload_images_hdfs(filename, img_url)
                if not new_img_url:
                    return jsonify({'failed': '上传hadoop失败，请重试！'})
                if int(is_show) == 1:
                    banner = Banner(banner_desc=desc, banner_img = new_img_url, is_show=is_show, putaway_time=putaway_time)
                else:
                    banner = Banner(banner_desc=desc, is_show=is_show, banner_img = new_img_url,)
                # banner = Banner(banner_desc = desc, banner_img = new_img_url, is_show=is_show)
                db.session.add(banner)
                db.session.commit()
                os.remove(img_url)
                return jsonify({"success": 'ok'})
        except Exception as e  :
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({'failed':'操作失败，请重试！'})

# 获取预览
@new_flash.route('/get_img_url', methods=['POST'])
@login_required
def get_img_url():
    if request.method == 'POST':
        try:
            import time
            uu = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            file_obj = request.files.get('file')
            base_pic = BASE_PIC + "/banner_" + uu + (file_obj.filename).replace(' ', '')
            base_pic_url = BASE_PIC_URL + "/banner_"+ uu + (file_obj.filename).replace(" ", "")
            with open(base_pic, 'wb') as f:
                for i in file_obj:
                    f.write(i)
            return jsonify({'success':'ok', 'img_url':base_pic, "base_pic_url":base_pic_url})
        except Exception as e:
            current_app.logger.error(e)
        return jsonify({'failed': 'ok'})

