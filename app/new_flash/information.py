from flask_login import login_required
from flask import request, render_template, jsonify, flash, abort, url_for, redirect, session, Flask, g, current_app
from . import new_flash
from app.models import NewInformation, InformationCategory, Banner, FootBar, ViewNoticeList
from cms_server import db, redis_store
import time, datetime, os, sys
from common import push_service
import json
from PIL import Image
from app.new_flash.hadoop_service import upload_info_images_hdfs
from ..utils.Pagination import Pagination
from ..utils.sphinxapi3_query_keyword import query_keyword


ORIGINAL = 'ren_gong'
SELECT_ID = 'select_id'

BASE_PIC = os.path.join(sys.path[0], "app", "static", "pic")
BASE_PIC_URL = '/static/pic'


# 资讯展示
@new_flash.route("/information_list", methods=['GET'])
@login_required
def information_list():
    try:
        filter_time = request.args.get('query_time')
        if filter_time:
            info_obj_list = NewInformation.query.filter_by(is_delete=0). \
                filter(NewInformation.create_time.ilike("%" + filter_time + "%")).order_by(
                NewInformation.create_time.desc())
            if request.args.get(SELECT_ID):
                select_id = int(request.args.get(SELECT_ID))
                if select_id == 1:
                    info_obj_list = NewInformation.query.filter_by(is_delete=0, is_show=1). \
                        filter(NewInformation.create_time.ilike("%" + filter_time + "%")).order_by(
                        NewInformation.create_time.desc())
                elif select_id == 2:
                    info_obj_list = NewInformation.query.filter_by(is_delete=0, is_show=0). \
                        filter(NewInformation.create_time.ilike("%" + filter_time + "%")).order_by(
                        NewInformation.create_time.desc())
                elif select_id == 3:
                    info_obj_list = NewInformation.query.filter_by(is_delete=0, source_name=ORIGINAL). \
                        filter(NewInformation.create_time.ilike("%" + filter_time + "%")).order_by(
                        NewInformation.create_time.desc())
                else:
                    info_obj_list = NewInformation.query.filter_by(is_delete=0).filter(
                        NewInformation.create_time.ilike("%" + filter_time + "%")).order_by(
                        NewInformation.create_time.desc())

        else:
            if request.args.get(SELECT_ID):
                select_id = int(request.args.get(SELECT_ID))
                if select_id == 1:
                    info_obj_list = NewInformation.query.filter_by(is_delete=0, is_show=1).order_by(
                        NewInformation.create_time.desc())
                elif select_id == 2:
                    info_obj_list = NewInformation.query.filter_by(is_delete=0, is_show=0).order_by(
                        NewInformation.create_time.desc())
                elif select_id == 3:
                    info_obj_list = NewInformation.query.filter_by(is_delete=0, source_name=ORIGINAL). \
                        order_by(NewInformation.create_time.desc())
                else:
                    info_obj_list = NewInformation.query.filter_by(is_delete=0).order_by(
                        NewInformation.create_time.desc())
            else:
                info_obj_list = NewInformation.query.filter_by(is_delete=0).order_by(NewInformation.create_time.desc())
        pager_obj = Pagination(request.args.get("page", 1), info_obj_list.count(), request.path, request.args,
                               per_page_count=10)
        data = info_obj_list[pager_obj.start:pager_obj.end]
        html = pager_obj.page_html()
        since_obj = NewInformation.query.filter_by(is_delete=0).order_by(NewInformation.create_time.desc()).first()
        info_since_id = since_obj.id
        cache_data = redis_store.get("add_auto_push_time_cache")
        if cache_data is not None:
            modal_data = json.loads((bytes.decode(cache_data)))
        else:
            modal_data = {"begin_time": "", "end_time": ""}
        return render_template('new_flash/new_flash_information.html', data=data, html=html, modal_data=modal_data,
                               info_since_id=info_since_id)
    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")


# 资讯关键字搜索
@new_flash.route('/information_search_result', methods=['GET'])
@login_required
def information_search_result():
    try:
        keyword = request.args.get("keyword")
        info_id_list = query_keyword("news_main news_delta", '@title %s' % keyword,
                                     current_app.config['SP_HOST'], current_app.config["SP_PORT"])
        info_obj_list = []
        for info_id in info_id_list:
            info_obj = NewInformation.query.filter(NewInformation.id == info_id).first()
            info_obj_list.append(info_obj)
        info_obj_list.sort(key=lambda info_obj: info_obj.create_time)
        info_obj_list.reverse()
        pager_obj = Pagination(request.args.get("page", 1), len(info_obj_list), request.path, request.args,
                               per_page_count=10)
        data = info_obj_list[pager_obj.start:pager_obj.end]
        html = pager_obj.page_html()
        return render_template("new_flash/info_search_result.html", data=data, html=html,
                               result_count=len(info_obj_list))
    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")


# 资讯定时查询
@new_flash.route('/timer_getting_info', methods=['GET'])
@login_required
def timer_getting_info():
    try:
        since_id = request.args.get("since_id")
        since_id = since_id if since_id else 0
        new_obj_count = NewInformation.query.filter(NewInformation.is_delete == 0, NewInformation.id > since_id).count()
        obj_count = new_obj_count if new_obj_count else 0
        return jsonify({"success": "ok", "obj_count": obj_count})
    except Exception as e:
        current_app.logger.error(e)
    return render_template("404.html")


# 初始加载获取id
@new_flash.route('/get_info_id', methods=['GET'])
@login_required
def get_info_id():
    try:
        initial_info_id = NewInformation.query.filter_by(is_delete=0).order_by(
            NewInformation.create_time.desc()).first()
        return jsonify({'success': 'ok', 'initial_info_id': initial_info_id.id})
    except Exception as e:
        current_app.logger.error(e)


# 编辑资讯
@new_flash.route("/modify_information", methods=['GET', 'POST'])
@login_required
def modify_information():
    if request.method == "GET":
        id = request.args.get('id', type=int)
        row = NewInformation.query.filter(NewInformation.id == id)
        category = InformationCategory.query
        footbar_list = FootBar.query.all()
        return render_template('new_flash/modify_new_information.html', data=row, rows=category,
                               footbar_list=footbar_list)
    elif request.method == "POST":
        try:
            info = NewInformation.query.filter_by(id=request.form['id']).first()
            notice_obj = ViewNoticeList.query.filter_by(original_id=request.form.get("id")).first()

            # 如果没有，该条info可能是在编辑状态下，修改了type。需新增notice。
            if not notice_obj:
                if request.form.get("content_type", type=int) not in [0, 1]:
                    try:
                        present_date = datetime.datetime.now().strftime("%Y-%m-%d")
                        notice_obj = ViewNoticeList(original_id=info.id, original_img=info.img,
                                                    original_type=info.content_type,
                                                    present_date=present_date)

                        db.session.add(notice_obj)
                    except Exception as e:
                        db.session.callback()
                        current_app.logger.error(e)
                        return jsonify({"success": "failed", "msg": '资讯写入NOTICE时，出现问题'})
            else:
                notice_obj.original_type = request.form.get("content_type", type=int)

            if request.files.get('img'):
                img_obj = request.files.get('img')
                img_url = request.form.get('img_url')
                base_pic_url = request.form.get('base_pic_url')
                filename = base_pic_url.replace("/static/pic/", '')
                new_img_url = upload_info_images_hdfs(filename, img_url)
                info.img = new_img_url
                # 修改notice相关数据
                if notice_obj:
                    notice_obj.original_img = new_img_url

                if not new_img_url:
                    return {'failed': '获取hadoop图片失败，请重试！'}
                os.remove(img_url)

            source_url = "" if not request.form.get("source_url") else request.form.get("source_url")
            info.title = request.form['title']
            info.content = request.form['content']
            info.category = request.form['category']
            info.is_show = request.form['is_show']
            info.tag = request.form["tag"]
            info.author = request.form["author"]
            info.remarks = request.form['remarks']
            info.source_name = request.form["source_name"]
            info.content_id = int(time.time()),
            info.update_time = datetime.datetime.now()
            info.source_url = source_url
            info.foot_bar_id = request.form.get("footbar_id")
            info.content_type = request.form.get("content_type", type=int)

            db.session.commit()

            data = {"id": info.id, "img": info.img, "title": info.title, "content": info.content,
                    "category": info.category, "is_show": info.is_show,
                    "tag": info.tag, "author": info.author, "remarks": info.remarks, "source_name": info.source_name,
                    "content_id": info.content_id, "update_time": str(info.update_time), "source_url": info.source_url}
            data = json.dumps(data)
            redis_store.lpush("cache_real_time_news", data)

            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({'failed': '未修改成功,请重试!'})


# 获取预览
@new_flash.route('/get_info_img_url', methods=['POST'])
@login_required
def get_info_img_url():
    if request.method == 'POST':
        try:
            import time
            uu = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            file_obj = request.files.get('file')
            fname, fext = os.path.splitext(file_obj.filename)
            base_pic = BASE_PIC + "/title_" + uu + fext
            base_pic_url = BASE_PIC_URL + "/title_" + uu + fext
            img = Image.open(file_obj)
            if len(img.split()) == 4:
                # prevent IOError: cannot write mode RGBA as BMP
                r, g, b, a = img.split()
                img = Image.merge("RGB", (r, g, b))
            img.thumbnail((268, 200), Image.ANTIALIAS)
            print(base_pic)
            print(base_pic_url)
            img.save(base_pic)
            return jsonify({'success': 'ok', 'img_url': base_pic, "base_pic_url": base_pic_url})
        except Exception as e:
            current_app.logger.error(e)
        return jsonify({'failed': 'ok'})


# 删除资讯
@new_flash.route("/delete_information", methods=['GET', 'POST'])
@login_required
def delete_information():
    if request.method == "POST":
        try:
            info = NewInformation.query.filter_by(id=request.form['id']).first()
            info.is_delete = 1
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify({'failed': 'ok'})


# 批量删除资讯
@new_flash.route("/delete_choice_information", methods=['GET', 'POST'])
@login_required
def delete_choice_information():
    if request.method == 'POST':
        try:
            id_list = request.get_data()
            id_list = json.loads(id_list.decode('utf-8'))
            for id in id_list:
                info = NewInformation.query.filter_by(id=int(id)).first()
                info.is_delete = 1
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify({'failed': 'ok'})


# 添加资讯
@new_flash.route("/add_information", methods=['GET', 'POST'])
@login_required
def add_information():
    if request.method == "GET":
        category = InformationCategory.query
        footbar_list = FootBar.query.all()
        return render_template('new_flash/add_new_information.html', rows=category, footbar_list=footbar_list)
    elif request.method == "POST":
        try:
            img_obj = request.files.get('img')
            img_url = request.form.get('img_url')
            base_pic_url = request.form.get('base_pic_url')
            filename = base_pic_url.replace("/static/pic/", '')
            source_url = request.form.get("source_url")
            content_type = request.form.get("content_type", type=int)
            c_time = request.form.get("create_time", "")

            create_time = c_time if c_time else datetime.datetime.now()

            if not source_url:
                source_url = ""
            new_img_url = upload_info_images_hdfs(filename, img_url)
            if not new_img_url:
                return jsonify({'msg': '获取hadoop图片失败，请重试！'})
            info = NewInformation(title=request.form['title'], content=request.form['content'],
                                  category=request.form['category'],
                                  is_show=request.form['is_show'], tag=request.form["tag"],
                                  author=request.form["author"],
                                  remarks=request.form['remarks'], source_name="ren_gong", content_id=int(time.time()),
                                  img=new_img_url, source_url=source_url, foot_bar_id=request.form["footbar_id"],
                                  content_type=content_type, create_time=create_time)
            db.session.add(info)
            db.session.commit()
            # original_type/content_type
            # 0:抓取资讯;1:原创;2:解盘;3:视频;4:音频;5:pdf;6:早报;7:晚报;
            if content_type not in [0,1]:
                try:
                    present_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    notice_obj = ViewNoticeList(original_id = info.id, original_img = info.img,
                                                original_type = info.content_type,
                                                present_date = present_date)
                    db.session.add(notice_obj)
                    db.session.commit()
                except Exception as e:
                    db.session.callback()
                    current_app.logger.error(e)
                    return jsonify({"success":"failed", "msg": '资讯写入NOTICE时，出现问题'})

            data = {"id": info.id, "img": info.img, "title": info.title, "content": info.content,
                    "category": info.category, "is_show": info.is_show,
                    "tag": info.tag, "author": info.author, "remarks": info.remarks, "source_name": info.source_name,
                    "content_id": info.content_id, "source_url": info.source_url, "foot_bar_id": info.foot_bar_id,
                    "content_type":info.content_type}
            data = json.dumps(data)
            redis_store.lpush("cache_real_time_news", data)

            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify({'success': 'failed', "msg":"保存过程中出错，请重试！！！"})


# 展示资讯
@new_flash.route("/show_information", methods=['GET', 'POST'])
@login_required
def show_information():
    if request.method == "POST":
        try:
            id = request.form['id']
            row = NewInformation.query.filter(NewInformation.id == id).first()
            if row.is_show != 1:
                row.is_show = 1
                db.session.commit()
                return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    else:
        return jsonify({'failed': 'ok'})


# 取消展示资讯
@new_flash.route("/close_information", methods=['GET', 'POST'])
@login_required
def close_information():
    if request.method == "POST":
        try:
            id = request.form['id']
            row = NewInformation.query.filter(NewInformation.id == id).first()
            if row.is_show != 0:
                row.is_show = 0
                row.is_push = 0
                db.session.commit()
                return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    else:
        return jsonify({'failed': 'ok'})


# 设定为banner
@new_flash.route("/set_banner", methods=['GET', 'POST'])
@login_required
def set_banner():
    if request.method == "POST":
        try:
            id = request.form['id']
            url = current_app.config["BANNER_DETAIL_URL"] + id
            if Banner.query.filter_by(skip_url=url).first():
                return jsonify({'failed': '该条资讯在banner模块已存在，请重新选择！'})
            info = NewInformation.query.filter_by(id=id).first()
            banner = Banner(banner_name=info.title, banner_desc=info.title, banner_img=info.img, skip_url=url)
            db.session.add(banner)
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    return jsonify({'failed': '操作失败，请重试！'})


# 资讯类别
@new_flash.route('/information_category', methods=['GET', 'POST'])
@login_required
def information_category():
    page = request.args.get('page', 1, type=int)
    pagination = InformationCategory.query.filter_by(is_delete=0).order_by(InformationCategory.id).paginate(page,
                                                                                                            per_page=10,
                                                                                                            error_out=False)
    data = pagination.items
    return render_template('new_flash/information_category.html', data=data, pagination=pagination)


# 编辑资讯类别
@new_flash.route("/modify_info_category", methods=['GET', 'POST'])
@login_required
def modify_info_category():
    if request.method == "GET":
        id = request.args.get('id', type=int)
        row = InformationCategory.query.filter(InformationCategory.id == id, InformationCategory.is_delete == 0)
        return render_template('new_flash/modify_info_category.html', data=row)
    elif request.method == "POST":
        info = InformationCategory.query.filter_by(id=request.form['id']).first()
        info.catname = request.form['catname']
        info.keyword = request.form['keyword']
        db.session.commit()
        return jsonify({'success': 'ok'})


# 添加资讯类别
@new_flash.route("/add_info_category", methods=['GET', 'POST'])
@login_required
def add_info_category():
    if request.method == "GET":
        return render_template('new_flash/add_info_category.html')
    elif request.method == "POST":
        info = InformationCategory(catname=request.form['catname'], keyword=request.form['keyword'], is_delete=0)
        db.session.add(info)
        db.session.commit()
        return jsonify({'success': 'ok'})


# 删除资讯类别
@new_flash.route("/delete_info_category", methods=['GET', 'POST'])
@login_required
def delete_info_category():
    if request.method == "POST":
        info = InformationCategory.query.filter_by(id=request.form['id']).first()
        info.is_delete = 1
        db.session.commit()
        return jsonify({'success': 'ok'})


# FootBar
@new_flash.route("/footbar_views", methods=['GET', 'POST'])
@login_required
def footbar_views():
    if request.method == "GET":
        page = request.args.get("page", 1, type=int)
        select_id = request.args.get("select_id", type=int)
        if select_id == 1:
            p = FootBar.query.filter_by(is_delete=0)
        elif select_id == 2:
            p = FootBar.query.filter_by(is_delete=1)
        else:
            p = FootBar.query
        pagination = p.order_by(FootBar.update_time.desc()).paginate(page, per_page=5, error_out=False)
        data = pagination.items
        return render_template("new_flash/foot_bar.html", data=data, pagination=pagination)


@new_flash.route("/add_footbar", methods=['GET', 'POST'])
@login_required
def add_footbar():
    if request.method == "GET":
        return render_template("new_flash/add_foot_bar.html")
    elif request.method == 'POST':
        try:
            content = request.form.get("content")
            fb_obj = FootBar(content=content, is_delete=0, update_time=datetime.datetime.now())
            db.session.add(fb_obj)
            db.session.commit()
            return jsonify({"success": "ok"})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({"success": 'failed'})


@new_flash.route("/modify_footbar", methods=['GET', 'POST'])
@login_required
def modify_footbar():
    fb_obj = FootBar.query.filter_by(id=request.args.get("id")).first()
    if request.method == "GET":
        if fb_obj:
            return render_template("new_flash/modify_foot_bar.html", data=fb_obj)
    elif request.method == 'POST':
        try:
            content = request.form.get("content", "")
            is_delete = request.form.get("is_delete")
            fb_obj.content = content
            fb_obj.is_delete = is_delete
            fb_obj.update_time = datetime.datetime.now()
            db.session.commit()
            return jsonify({"success": "ok"})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({"success": 'failed'})


# 删除单条FootBar
@new_flash.route("/delete_footbar", methods=["POST"])
@login_required
def delete_footbar():
    try:
        if request.method == 'POST':
            foot_bar = FootBar.query.filter_by(id=request.form['id']).first()
            foot_bar.is_delete = 1
            db.session.commit()
            return jsonify({'success': 'ok'})
    except Exception as e:
        current_app.logger.error(e)


# 下架多条banner
@new_flash.route("/delete_choice_footbar", methods=["GET", "POST"])
@login_required
def delete_choice_footbar():
    if request.method == 'POST':
        try:
            id_list = request.get_data()
            id_list = json.loads(id_list.decode('utf-8'))
            for id in id_list:
                info = FootBar.query.filter_by(id=int(id)).first()
                info.is_delete = 1
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
        return jsonify({'failed': 'ok'})
