from flask_login import login_required
from flask import request, render_template, jsonify, current_app
from . import crawl
from .. import models
from cms_server import db
import json


@crawl.route("/crawler", methods=["GET"])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    pagination = models.SpidersVisualizatonBase.query.filter().paginate(page, per_page=12, error_out=False)
    data = pagination.items
    # data = models.SpidersVisualizatonBase.query.filter().all()
    return render_template("crawler/crawler_list.html", data=data, pagination=pagination)


# 添加新的target_url
@crawl.route("/crawler/add_target_url", methods=["GET","POST"])
@login_required
def add_target_url():
    if request.method == "GET":
        return render_template("crawler/add_target_url.html")
    elif request.method == "POST":
        try:
            spider_ch_name = request.form.get("spider_ch_name")
            spider_en_name = request.form.get("spider_en_name")
            target_url = request.form.get("target_url")
            req_headers = request.form.get("req_headers")
            information_type = request.form.get("information_type")
            req_method = request.form.get("req_method")
            req_params = request.form.get("req_params")
            req_code = request.form.get("req_code")
            fliter_a_tag = request.form.get("fliter_a_tag")
            img_watermark = request.form.get("img_watermark")
            ls_rule_type = request.form.get("ls_rule_type")
            html_ls_tag = request.form.get("html_ls_tag")
            time_interval = request.form.get("time_interval")
            is_userful = request.form.get("is_userful")
            get_num = request.form.get("get_num")
            base1 = models.SpidersVisualizatonBase(spider_ch_name=spider_ch_name, spider_en_name=spider_en_name,
                                                   target_url=target_url, req_headers=req_headers,
                                                   information_type=int(information_type),
                                                   req_method=req_method, req_params=req_params,
                                                   req_code=req_code, fliter_a_tag=fliter_a_tag,
                                                   img_watermark=img_watermark, ls_rule_type=ls_rule_type,
                                                   html_ls_tag=html_ls_tag, time_interval=time_interval,
                                                   is_userful=is_userful, get_num=get_num)
            db.session.add(base1)
            db.session.commit()
            # 保存进可视化规则表
            dic1 = {"内容":1, "标题":2, "详情链接":3, "作者":4}
            dic2 = {"内容":"content", "标题":"title", "详情链接":"details_url", "作者":"author"}
            base_id = base1.id
            field = json.loads(request.form.get("field"))
            for f in field:
                ch_name = f["ch_name"]
                column_type = dic1[ch_name]
                en_name = dic2[ch_name]
                get_column_rule = f["get_column_rule"]
                get_data_way = f["get_data_way"],
                start_for = f["start_for"],
                analysis_code = f["analysis_code"]
                # 以下字段还没增加先设为0
                column_rule_type = 0
                find_all = 0
                column_attribute = 0
                rule1 = models.SpidersVisualizationRule(base_id=base_id,ch_name=ch_name,en_name=en_name,
                                                        column_type=column_type, get_column_rule=get_column_rule,
                                                        get_data_way=get_data_way,start_for=start_for,
                                                        analysis_code=analysis_code, column_rule_type=column_rule_type,
                                                        find_all=find_all, column_attribute=column_attribute)
                db.session.add(rule1)
                db.session.commit()
                # 保存进可视化数据预处理表
                rule_id = rule1.id
                for i in f["all_item"]:
                    if i["type"] != "0":
                        type = i["type"]
                        delete_tag = i["delete_tag"]
                        replace_tag = i["replace_tag"]
                        end_replace_tag = i["end_replace_tag"]
                        handle = models.SpidersVisualizationDataHandle(rule_id=rule_id, type=type, delete_tag=delete_tag,
                                                                 replace_tag=replace_tag, end_replace_tag=end_replace_tag)
                        db.session.add(handle)
                        db.session.commit()
            return jsonify({"success": "ok"})
        except Exception as e:
            current_app.logger.error("crawler_views.py - add_target_url is error!", e)
            return jsonify({"failed": "添加target_url发生错误，请重试"})


# 删除target_url
@crawl.route("/crawler/delete_target_url", methods=["GET", "POST"])
@login_required
def delete_target_url():
    if request.method == "GET":
        try:
            print(request.args.get("type"))
            if int(request.args.get("type")) == 1:
                h_id = request.args.get("h_id")
                handle = models.SpidersVisualizationDataHandle.query.filter(models.SpidersVisualizationDataHandle.id==int(h_id)).first()
                db.session.delete(handle)
                db.session.commit()
                return jsonify({"success": "ok"})
            else:
                r_id = request.args.get("r_id")
                rule_data = models.SpidersVisualizationRule.query.filter_by(id=r_id).first()
                db.session.delete(rule_data)
                db.session.commit()
                handle_infos = models.SpidersVisualizationDataHandle.query.filter(models.SpidersVisualizationDataHandle.rule_id==r_id).all()
                for handle in handle_infos:
                    db.session.delete(handle)
                    db.session.commit()
                return jsonify({"success": "ok"})
        except Exception as e:
            return jsonify({"failed": "删除不成功，请重试"})
    elif request.method == "POST":
        try:
            b_id = request.form.get("b_id")
            url_data = models.SpidersVisualizatonBase.query.filter_by(id=b_id).first()
            db.session.delete(url_data)
            db.session.commit()
            rule_datas = models.SpidersVisualizationRule.query.filter(models.SpidersVisualizationRule.base_id==b_id).all()
            for d in rule_datas:
                db.session.delete(d)
                db.session.commit()
                rule_id = d.id
                handle_datas = models.SpidersVisualizationDataHandle.query.filter(models.SpidersVisualizationDataHandle.rule_id==rule_id).all()
                for h in handle_datas:
                    db.session.delete(h)
                    db.session.commit()
            return jsonify({"success": "ok"})
        except Exception as e:
            return jsonify({"failed": "删除不成功，请重试"})


# 修改目标爬虫内容
@crawl.route("/crawler/modify_target_url", methods=["GET", "POST"])
@login_required
def modify_target_url():
    if request.method == "GET":
        b_id = request.args.get("id")
        base_data = models.SpidersVisualizatonBase.query.filter(models.SpidersVisualizatonBase.id==int(b_id)).first()
        rule_datas = models.SpidersVisualizationRule.query.filter(models.SpidersVisualizationRule.base_id==int(b_id)).all()
        handle_datas = []
        for d in rule_datas:
            data = models.SpidersVisualizationDataHandle.query.filter(models.SpidersVisualizationDataHandle.rule_id==d.id).all()
            if data:
                handle_datas.append(data)
        return render_template("/crawler/modify_target_url.html", base_data=base_data, rule_datas=rule_datas, handle_datas=handle_datas)
    elif request.method == "POST":
        try:
            # 更新爬虫可视化基础表
            base_info = models.SpidersVisualizatonBase.query.filter(models.SpidersVisualizatonBase.id == request.form.get("id")).first()
            base_info.spider_ch_name = request.form.get("spider_ch_name")
            base_info.spider_en_name = request.form.get("spider_en_name")
            base_info.target_url = request.form.get("target_url")
            base_info.req_headers = request.form.get("req_headers")
            base_info.information_type = request.form.get("information_type")
            base_info.req_method = request.form.get("req_method")
            base_info.req_params = request.form.get("req_params")
            base_info.req_code = request.form.get("req_code")
            base_info.fliter_a_tag = request.form.get("fliter_a_tag")
            base_info.img_watermark = request.form.get("img_watermark")
            base_info.ls_rule_type = request.form.get("ls_rule_type")
            base_info.html_ls_tag = request.form.get("html_ls_tag")
            base_info.time_interval = request.form.get("time_interval")
            base_info.is_userful = request.form.get("is_userful")
            base_info.get_num = request.form.get("get_num")
            db.session.commit()
            # 更新可视化规则表
            rule_infos = models.SpidersVisualizationRule.query.filter(models.SpidersVisualizationRule.base_id == base_info.id).all()
            dic1 = {"内容":1, "标题":2, "详情链接":3, "作者":4}
            dic2 = {"内容":"content", "标题":"title", "详情链接":"details_url", "作者":"author"}
            field = json.loads(request.form.get("field"))
            for f in field:
                if int(f["r_id"]) == -1:
                    column_type = dic1[f["ch_name"]]
                    en_name = dic2[f["ch_name"]]
                    rule_data = models.SpidersVisualizationRule(base_id=base_info.id, ch_name=f["ch_name"],
                                                                en_name=en_name, column_type=column_type,
                                                                get_column_rule=f["get_column_rule"],
                                                                get_data_way=f["get_data_way"], start_for=f["start_for"],
                                                                analysis_code=f["analysis_code"])
                    db.session.add(rule_data)
                    db.session.commit()
                for info in rule_infos:
                    if int(f["r_id"]) == info.id:
                        info.ch_name = f["ch_name"]
                        info.column_type = dic1[f["ch_name"]]
                        info.en_name = dic2[f["ch_name"]]
                        info.get_column_rule = f["get_column_rule"]
                        info.get_data_way = f["get_data_way"],
                        info.start_for = f["start_for"],
                        info.analysis_code = f["analysis_code"]
                        db.session.commit()
                        continue
            # 保存进可视化数据预处理表
            for f in field:
                handel_infos = models.SpidersVisualizationDataHandle.query.filter(models.SpidersVisualizationDataHandle.rule_id==int(f["r_id"])).all()
                for i in f["all_item"]:
                    if i["h_id"] == -1:
                        handle = models.SpidersVisualizationDataHandle(rule_id=f["r_id"], type=i["type"],
                                                                       delete_tag=i["delete_tag"],
                                                                       replace_tag=i["replace_tag"],
                                                                       end_replace_tag=i["end_replace_tag"])
                        db.session.add(handle)
                        db.session.commit()
                        continue
                    for info in handel_infos:
                        if i["type"] != "0" and int(i["h_id"]) == info.id:
                            info.type = i["type"]
                            info.delete_tag = i["delete_tag"]
                            info.replace_tag = i["replace_tag"]
                            info.end_replace_tag = i["end_replace_tag"]
                            db.session.commit()
                            continue
            return jsonify({"success": "ok"})
        except Exception as e:
            current_app.logger.error("crawler_views.py - add_target_url is error!", e)
            return jsonify({"failed": "添加target_url发生错误，请重试"})


