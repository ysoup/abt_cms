from . import rep

from flask_login import login_required
from flask import request, render_template, jsonify, flash, abort, url_for, redirect, session, Flask, g, current_app
from .. import models
from cms_server import db, redis_store
import time, copy
from common import push_service
import json, datetime, os, sys, base64
from common.kline import get_top_kline, get_index_data
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# original_type/content_type
# 0:抓取资讯;1:原创;2:解盘;3:视频;4:音频;5:pdf;6:早报;7:晚报;

# PaperMorningUrl = "/static/global/paper_morning.png"
# PaperEveningUrl = "/static/global/paper_evening.png"
PaperMorningUrl = "/aibicloud/images/ckup_20181025_200019.png"
PaperEveningUrl = "/aibicloud/images/ckup_20181025_200055.png"


@rep.route('/rep_list', methods=['GET'])
@login_required
def rep_list():
    try:
        page = request.args.get('page', 1, type=int)
        pagination = models.Report.query.filter(models.Report.is_delete == 0).order_by(
            models.Report.update_time.desc()).paginate(page, per_page=2, error_out=False)
        data = pagination.items
        select_id = 0
        g.select_id = select_id
        return render_template("report/report_list.html", data=data, pagination=pagination)
    except Exception as e:
        current_app.logger.error(e)


@rep.route('/add_rep', methods=['GET', 'POST'])
@login_required
def add_rep():
    if request.method == 'GET':
        source_list = models.IndexSource.query.filter_by(is_delete=0)
        current_hour = datetime.datetime.now().strftime("%H")
        return render_template("report/add_report.html", rows=source_list, current_hour=current_hour)
    elif request.method == 'POST':
        try:
            c_type = request.form.get('rep_type', 1, type=int)
            content = request.form.get("content")
            top_source_id = int(request.form.get("top_source"))
            sec_source_id = json.loads(request.form.get("sec_source"))
            result_sec_source = [int(i) for i in sec_source_id]
            # now_time = datetime.datetime.now()
            rep_obj = models.Report(type=c_type, content=content, top_source_id=top_source_id, information_id=0)
            # rep_obj = models.Report(type=c_type, content=content, top_source_id=top_source_id, create_time=now_time, update_time=now_time)
            for sec_id in result_sec_source:
                sec_obj = models.IndexSource.query.filter_by(id=sec_id).first()
                rep_obj.sec_source.append(sec_obj)
            try:
                prefix_name = "爱必早报" if c_type == 1 else "爱必晚报"
                date_time = datetime.datetime.now().strftime("%m{}%d{}").format("月", "日")
                title = prefix_name + "" + date_time
                content_type = 6 if c_type == 1 else 7

                if content_type == 6:
                    img = PaperMorningUrl# 早报地址
                elif content_type == 7:
                    img = PaperEveningUrl# 晚报地址
                else:
                    img = ""

                info = models.NewInformation(title=title, content="",
                                             category=7,is_push=0,
                                             is_show=0, tag="Report",
                                             source_name="ren_gong",
                                             content_id=int(time.time()), img=img,
                                             foot_bar_id=0, content_type=content_type)
                db.session.add(info)
                db.session.commit()
                rep_obj.information_id = info.id
            except Exception as e:
                current_app.logger.error("Report未保存到资讯 -- ", e)
                db.session.rollback()
                return jsonify({"success": "failed", "msg": "Report保存到资讯过程中，出现问题。"})
            db.session.add(rep_obj)
            db.session.commit()

            return jsonify({'success': 'ok'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)


@rep.route('/modify_rep', methods=['GET', 'POST'])
@login_required
def modify_rep():
    if request.method == 'GET':
        try:
            source_list = models.IndexSource.query.filter_by(is_delete=0)
            rep_id = request.args.get("id")
            rep_obj = models.Report.query.filter_by(id=rep_id).first()

            return render_template("report/modify_report.html", data=rep_obj, rows=source_list)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify({'failed': '读取失败，请重试'})
    elif request.method == 'POST':
        try:
            # 获取到当前Report info_id，修改title, content
            info_id = request.form.get("info_id",type=int)
            c_type = request.form.get('rep_type', 1, type=int)
            content = request.form.get("content")
            if info_id:
                info_obj = models.NewInformation.query.filter_by(id=info_id).first()
                if not info_obj:
                    return jsonify({"success": "failed", "msg": "未获取到相关资讯"})
                try:
                    # 相关资讯变更
                    content_type = 6 if c_type == 1 else 7
                    prefix_name = "爱必早报" if c_type == 1 else "爱必晚报"
                    date_time = datetime.datetime.now().strftime("%m{}%d{}").format("月", "日")
                    title = prefix_name + "" + date_time
                    info_obj.title = title
                    # info_obj.content = ""
                    info_obj.content_type = content_type
                    info_obj.update_time = datetime.datetime.now()
                except Exception as e:
                    current_app.logger.error(e)
                    return jsonify({"success":"ok", "msg":"修改相关资讯出错"})
            rep_id = request.form.get("id")
            rep_obj = models.Report.query.filter_by(id=rep_id).first()
            if rep_obj:
                top_source_id = int(request.form.get("top_source"))

                sec_source_id = json.loads(request.form.get("sec_source"))
                result_sec_source = [int(i) for i in sec_source_id]

                rep_obj.type = c_type
                rep_obj.content = content
                rep_obj.top_source_id = top_source_id
                rep_obj.update_time = datetime.datetime.now()
                l = []
                for sec_id in result_sec_source:
                    sec_obj = models.IndexSource.query.filter_by(id=sec_id).first()
                    l.append(sec_obj)
                    rep_obj.sec_source = l
                db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({"success": "ok", "msg": "编辑Report出错"})


@rep.route("/delete_rep", methods=['GET', 'POST'])
@login_required
def delete_rep():
    if request.method == "POST":
        try:
            info = models.Report.query.filter_by(id=request.form['id']).first()
            info.is_delete = 1
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({'failed': 'ok'})

# 折线图
@rep.route("/download_rep", methods=["GET", "POST"])
def download_rep():
    if request.method == 'GET':
        try:
            index_list = []
            rep_id = request.args.get('id')
            rep_obj = models.Report.query.filter_by(id=rep_id).first()
            top_source_name = models.IndexSource.query.filter_by(id=rep_obj.top_source_id).first().source_name
            index_list.append(top_source_name)
            sec_list = []
            for sec_obj in rep_obj.sec_source:
                index_list.append(sec_obj.source_name)
                sec_list.append(sec_obj.source_name)
            index_data = get_index_data(index_list)
            # sec_list = json.dumps(sec_list)
            if rep_obj:
                return render_template("aibipaper/aibipaper.html", data=rep_obj, sec_list=sec_list,
                                       top_source_name=top_source_name, index_data=index_data, ab_type=rep_obj.type, info_id = rep_obj.information_id)
            else:
                return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
    elif request.method == 'POST':
        try:
            rep_obj = models.Report.query.filter_by(id=request.form.get("id")).first()
            source_id = rep_obj.top_source_id
            source_name = models.IndexSource.query.filter_by(id=source_id).first().source_name
            since_date = time.strftime("%Y%m%d", time.localtime())
            since_time = time.strftime("%H:%M:%S")
            res = get_top_kline("AIBILINK", "INDEX_" + source_name, "15min", "96", since_date, since_time)
            x_l = []
            y_l = []
            for r in res:
                y_l.insert(0, r.get('close'))
                r_x = r.get('time')[:5]
                x_l.insert(0, r_x)
            x = x_l
            y = y_l
            start_point = x[0]
            end_port = x[-1]
            if start_point < end_port:
                line_color = "#f01616"
                fill_color = "#ffebeb"
            else:
                line_color = "#139b23"
                fill_color = "#e5f5ea"
            plt.figure(figsize=(8, 3), dpi=96)
            # plt.figure(figsize=(6, 2), dpi=72)

            axes = plt.subplot(111)
            axes.set_xticks([])
            axes.set_yticks([])
            axes.spines['top'].set_visible(False)
            axes.spines['right'].set_visible(False)
            axes.spines['bottom'].set_visible(False)
            axes.spines['left'].set_visible(False)
            axes.plot(x, y, color=line_color)
            min_y = min(y) - 6

            # current_app.logger.info("download_rep === y,min_y %s %s"%(y, min_y))

            plt.fill_between(x, y, min_y, interpolate=True, color=fill_color, alpha=1)

            img_url = os.path.join(sys.path[0], "app", "static", "paper", 'paper_img.png')
            if os.path.exists(img_url):
                os.remove(img_url)
                print('del pic. Url=%s.'%img_url)
            plt.savefig(img_url, bbox_inches='tight')
            load_path = "/static/paper/paper_img.png"
            if img_url:
                return jsonify({"success": "ok", "img_url": load_path})
            else:
                return jsonify({"failed": '图片在上传服务器时遇到错误，请重试'})
        except Exception as e:
            current_app.logger.error(e)


@rep.route("/convert_img", methods=['POST'])
def convert_img():
    if request.method == 'POST':
        try:
            img_base = request.form.get("img_b")
            img_data = base64.b64decode(img_base[23:])
            missing_padding = 4 - len(img_data) % 4
            if missing_padding:
                img_data += b'=' * missing_padding
            date_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            img_name = 'aibipaper_%s.png' % date_time
            img_url = os.path.join(sys.path[0], "app", "static", "paper", img_name)
            if os.path.exists(img_url):
                os.remove(img_url)
            file = open(img_url, 'wb')
            file.write(img_data)
            file.close()
            final_img_path = "/static/paper/%s" % img_name
            if final_img_path:
                from ..new_flash.hadoop_service import upload_images_hdfs
                new_img_url = upload_images_hdfs(img_name, img_url)
                if not new_img_url:
                    return {'failed': '获取hadoop图片失败，请重试！'}
                os.remove(img_url)

                # 写入view_notice_list表。
                # ab_typye, info_id
                try:
                    ab_type = request.form.get("ab_type", type=int)
                    if ab_type == 1:    # 早报
                        original_type = 6

                    elif ab_type == 3:  # 晚报
                        original_type = 7
                    else :
                        return jsonify({"success": "failed", "msg": "Report Type错误"})

                    present_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    notice_obj = models.ViewNoticeList.query.filter_by(original_id=request.form.get("info_id")).first()
                    info_obj = models.NewInformation.query.filter_by(id=request.form.get("info_id")).first()
                    if info_obj:
                        if not notice_obj:
                            # 新增
                            notice_obj = models.ViewNoticeList(original_id=request.form.get("info_id"),
                                                               original_img=new_img_url, original_type=original_type,
                                                               present_date=present_date)
                            db.session.add(notice_obj)
                        else :
                            # 编辑
                            notice_obj.original_img = new_img_url
                            notice_obj.original_type = original_type
                            notice_obj.present_date = present_date
                        info_obj.content = '<div style="text-align: center;"><img alt="" src="%s" /></div>' %new_img_url
                    db.session.commit()
                except Exception as e :
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"success":"failed", "msg": "数据写入Notice失败"})
                return jsonify({"success": 'ok', "img": new_img_url})

        except Exception as e:
            current_app.logger.error(e)
            return jsonify({"failed": "下载过程中出现问题，请重试。"})


            # service_args = []
            # service_args.append('--disk-cache=yes')  ##开启缓存
            # service_args.append('--ignore-ssl-errors=true')
            # service_args.append('--ssl-protocol=TLSv1')
            # driver = webdriver.PhantomJS(service_args=service_args)
            # driver.set_window_size(cur_width, cur_height)
            # driver.implicitly_wait(10)
            # driver.set_page_load_timeout(10)
            # req_url = current_app.config["PAPER_LOAD"] + chi_url
            # driver.get(req_url)
            # # driver.get("https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd=111&rsv_pq=a97aa4be000363f5&rsv_t=4dc7%2BBBLKZ6jqnpepB4tpB9aAoV0T8RIMaW3DjJDSWLU2xT%2BVh6kDTHYGt4&rqlang=cn&rsv_enter=1&rsv_sug3=3&rsv_sug1=3&rsv_sug7=101")
            # img_url = os.path.join(sys.path[0], "app", "static", "paper", "paper_img.png")
            # if os.path.exists(img_url):
            #     os.remove(img_url)
            # driver.save_screenshot(img_url)
            # load_path = "/static/paper/paper_img.png"
            # driver.service.process.send_signal(signal.SIGTERM)
            # driver.quit()
            #     if img_url:
            #         return jsonify({"success":"ok", "img_url":load_path})
            #     else:
            #         return jsonify({"failed":'图片在上传服务器时遇到错误，请重试或者联系管理员'})
            # except Exception as e :
            #     current_app.logger.error(e)
            # finally:
            # driver.quit()
            # driver.service.process.send_signal(signal.SIGTERM)
            # driver.quit()


@rep.route('/source_list', methods=['GET'])
@login_required
def source_list():
    page = request.args.get('page', 1, type=int)
    pagination = models.IndexSource.query.filter_by(is_delete=0).\
        order_by(models.IndexSource.id).paginate(page, per_page=10, error_out=False)
    data = pagination.items
    return render_template("report/source_index.html", data=data, pagination=pagination)


@rep.route("/delete_source", methods=['GET', 'POST'])
@login_required
def delete_source():
    if request.method == "POST":
        try:
            info = models.IndexSource.query.filter_by(id=request.form['id']).first()
            info.is_delete = 1
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({'failed': 'ok'})


@rep.route('/add_source', methods=['GET', 'POST'])
@login_required
def add_source():
    if request.method == 'GET':
        return render_template("report/add_source.html")
    elif request.method == 'POST':
        try:
            source_obj = models.IndexSource(source_name=request.form['source_name'],
                                            update_time=datetime.datetime.now())
            db.session.add(source_obj)
            db.session.commit()
            return jsonify({"success": "ok"})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify({"failed": "ok"})


@rep.route("/modify_source", methods=['GET', 'POST'])
@login_required
def modify_source():
    if request.method == 'GET':
        source_id = request.args.get("id")
        source_obj = models.IndexSource.query.filter_by(id=source_id).first()
        return render_template("report/modify_source.html", data=source_obj)
    elif request.method == 'POST':
        try:
            info = models.IndexSource.query.filter_by(id=request.form['id']).first()
            info.source_name = request.form['source_name']
            info.update_time = datetime.datetime.now()
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)