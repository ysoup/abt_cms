import datetime, json
from flask_login import login_required
from flask import request, render_template, jsonify, flash, abort, url_for, redirect, session, Flask, g, current_app
from cms_server import db
from . import cal
from app import models
from ..utils.Pagination import Pagination


@cal.route("/calendar", methods=["GET"])
@login_required
def index():
    select_date = request.args.get("select_date")
    select_id = request.args.get('select_id')
    if select_id == str(1):
        event_list = models.Events.query.filter(models.Events.is_show == 1).order_by(models.Events.update_time.desc()).all()
    elif select_id == str(2):
        event_list = models.Events.query.filter(models.Events.is_show == 0).order_by(models.Events.update_time.desc()).all()
    else:
        event_list = models.Events.query.order_by(models.Events.update_time.desc()).all()
    if select_date:
        event_list = models.Events.query.filter(models.Events.happened_date==select_date).order_by(models.Events.update_time.desc()).all()
    coin_list = models.CoinBaseInfo.query.all()
    country_list = models.CountryInfo.query.all()
    exchange_list = models.ExchangeInfo.query.all()
    sub_list = models.Subjects.query.all()
    page_obj = Pagination(request.args.get("page", 1), len(event_list), request.path, request.args, per_page_count=10)
    data = event_list[page_obj.start:page_obj.end]
    html = page_obj.page_html()
    return render_template("calendar/calendar.html", data=data, sub_list=sub_list, coin_list=coin_list, country_list=country_list, exchange_list=exchange_list, html=html)  # subjects=subjects,


@cal.route('/calendar/get_tag_type', methods=['GET'])
@login_required
def get_tag_type():
    tag_type = int(request.args.get("tag_type", 1))
    eng_list = []
    if tag_type == 2:
        tag_info_list = models.CoinBaseInfo.query.all()
        [eng_list.append(tag_info.code) for tag_info in tag_info_list]
    elif tag_type == 3:
        tag_info_list = models.ExchangeInfo.query.all()
        [eng_list.append(tag_info.chinese_name) for tag_info in tag_info_list]
    else:
        tag_info_list = models.CountryInfo.query.all()
        [eng_list.append(tag_info.chinese_name) for tag_info in tag_info_list]
    return jsonify({'success':"ok","eng_list":eng_list})


@cal.route("/calendar/add_sub", methods=['POST'])
@login_required
def add_sub():
    if request.method == "POST":
        try:
            sub_name = request.form.get("sub_name")
            if sub_name:
                sub_obj = models.Subjects(name=sub_name)
                db.session.add(sub_obj)
                db.session.commit()
                return jsonify({"success":'ok'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
        return render_template("404.html")


@cal.route("/calendar/get_event_relation")
@login_required
def get_event_relation():
    choice_sub_id = request.args.get("choice_sub_id", 1)
    event_obj_list = models.Subjects.query.filter_by(id=choice_sub_id).first().sub_event
    event_id_list = []
    for event_obj in event_obj_list:
        event_id_list.append(event_obj.id)
    return jsonify({"success":"ok", "event_id_list":event_id_list})


@cal.route("/calendar/add_event_relation", methods=["GET", "POST"])
@login_required
def add_event_relation():
    if request.method == "GET":
        event_list = models.Events.query.order_by(models.Events.create_time.desc()).all()
        coin_list = models.CoinBaseInfo.query.all()
        country_list = models.CountryInfo.query.all()
        exchange_list = models.ExchangeInfo.query.all()
        sub_list = models.Subjects.query.all()
        return render_template("calendar/add_event_relation.html", sub_list=sub_list, data=event_list, coin_list=coin_list, country_list=country_list, exchange_list=exchange_list)
    elif request.method == 'POST':
        try:
            sub_id = request.form.get("sub_id")
            event_id_list = json.loads(request.form.get("event_id_list"))
            sub_obj = models.Subjects.query.filter_by(id=sub_id).first()
            event_obj_list = []
            for event_id in event_id_list:
                event_obj_list.append(models.Events.query.filter_by(id=event_id).first())
            sub_obj.sub_event = event_obj_list
            db.session.commit()
            return jsonify({"success":"ok"})
        except Exception as e :
            db.session.rollback()
            current_app.logger.error(e)
        return render_template("404.html")


@cal.route("/calendar/add_new_event", methods=["GET", "POST"])
@login_required
def add_new_event():
    if request.method == "GET":
        flash_data = models.NewFlashInformation.query.filter(models.NewFlashInformation.is_delete==0).order_by(models.NewFlashInformation.update_time.desc()).limit(600)
        info_data = db.session.query(models.NewInformation.id, models.NewInformation.source_url, models.NewInformation.title, models.NewInformation.update_time).filter(models.NewInformation.is_delete == 0).order_by(
        models.NewInformation.update_time.desc()).limit(200)
        country_info_list = models.CountryInfo.query.all()
        sub_list = models.Subjects.query.all()
        return render_template("calendar/add_new_event.html", flash_data=flash_data, info_data=info_data,country_info_list=country_info_list,sub_list=sub_list)
    elif request.method == "POST":
        try:
            # sub_id = request.form.get("sub")
            c_date = request.form.get('c_date')
            c_time = request.form.get("c_time")
            tag_type = request.form.get("tag_type")
            tag_name = request.form.get("tag_name")
            content = request.form.get("content", "")
            c_importance = request.form.get("c_importance")
            is_show = request.form.get("is_show")
            key_word = request.form.get("key_word")
            key_word = key_word if key_word else " "
            flash_id_list = json.loads(request.form.get("flash_id_list"))
            info_id_list = json.loads(request.form.get("info_id_list"))
            now_time = datetime.datetime.now()
            event_obj = models.Events(content=content, happened_date=c_date, happened_time=c_time,
                                      happened_tag_type=tag_type, happened_tag_id=tag_name, importance = c_importance,
                                      keywords=key_word, is_show=is_show, create_time=now_time, update_time=now_time)
            for flash_id in flash_id_list:
                flash_obj = models.NewFlashInformation.query.filter_by(id=flash_id).first()
                event_obj.event_news.append(flash_obj)
            for info_id in info_id_list:
                info_obj = models.NewInformation.query.filter_by(id=info_id).first()
                event_obj.event_info.append(info_obj)
            db.session.add(event_obj)
            db.session.commit()
            return jsonify({"success":"ok"})
        except Exception as e :
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify({"failed":'添加失败，请重试'})


@cal.route("/calendar/modify_event", methods=["GET", "POST"])
@login_required
def modify_event():
    if request.method == "GET":
        event_id = request.args.get("event_id")
        event_obj = models.Events.query.filter(models.Events.id == event_id).first()
        flash_data = models.NewFlashInformation.query.filter(models.NewFlashInformation.is_delete == 0).order_by(
            models.NewFlashInformation.update_time.desc()).limit(600)
        # info_data = models.NewInformation.query.filter(models.NewInformation.is_delete == 0).order_by(
        #     models.NewInformation.update_time.desc()).limit(1000)
        info_data = db.session.query(models.NewInformation.id, models.NewInformation.source_url, models.NewInformation.title, models.NewInformation.update_time).filter(models.NewInformation.is_delete == 0).order_by(
        models.NewInformation.update_time.desc()).limit(200)
        coin_list = models.CoinBaseInfo.query.all()
        country_list = models.CountryInfo.query.all()
        exchange_list = models.ExchangeInfo.query.all()
        sub_list = models.Subjects.query.all()
        new_id_list = []
        for new_obj in event_obj.event_news:
            new_id_list.append(new_obj.id)
        info_id_list = []
        for info_obj in event_obj.event_info:
            info_id_list.append(info_obj.id)
        if event_obj:
            tag_type = event_obj.happened_tag_type
            if tag_type == 1:
                tag_data = country_list
            elif tag_type == 2 :
                tag_data = coin_list
            elif tag_type == 3:
                tag_data = exchange_list

            return render_template("calendar/modify_event.html",event_obj=event_obj, coin_list=coin_list, country_list=country_list,
                                   exchange_list=exchange_list, tag_data = tag_data, sub_list=sub_list, flash_data=flash_data, info_data=info_data,
                                   info_id_list=info_id_list, new_id_list=new_id_list)

    elif request.method == "POST":
        try:
            event_id = request.form.get("event_id")
            c_date = request.form.get('c_date')
            c_time = request.form.get("c_time")
            tag_type = request.form.get("tag_type")
            tag_name = request.form.get("tag_name")
            content = request.form.get("content")
            c_importance = request.form.get("c_importance")
            is_show = request.form.get("is_show")
            key_word = request.form.get("key_word")
            key_word = key_word if key_word else " "
            flash_id_list = json.loads(request.form.get("flash_id_list"))
            info_id_list = json.loads(request.form.get("info_id_list"))
            now_time = datetime.datetime.now()
            event_obj = models.Events.query.filter(models.Events.id == event_id).first()
            if event_obj:
                event_obj.content = content
                event_obj.happened_date = c_date
                event_obj.happened_time = c_time
                event_obj.happened_tag_type = tag_type
                event_obj.happened_tag_id = tag_name
                event_obj.importance = c_importance
                event_obj.keywords = key_word
                event_obj.is_show = is_show
                event_obj.create_time = now_time
                event_obj.update_time = now_time
                flash_obj_list = []
                for flash_id in flash_id_list:
                    flash_obj = models.NewFlashInformation.query.filter_by(id=int(flash_id)).first()
                    flash_obj_list.append(flash_obj)
                    event_obj.event_news = flash_obj_list
                info_obj_list = []
                for info_id in info_id_list:
                    info_obj = models.NewInformation.query.filter_by(id=int(info_id)).first()
                    info_obj_list.append(info_obj)
                    event_obj.event_info = info_obj_list
                db.session.commit()
                return jsonify({"success": "ok"})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
        return render_template("404.html")


# search keyword
# @cal.route('/calendar/event_search_result', methods=['GET'])
# @login_required
# def new_search_result():
#     try:
#         keyword = request.args.get("keyword")
#         return "hello world"
#     except Exception as e:
#         current_app.logger.error(e)
#     return render_template("calendar/calendar.html")

# modify event state
@cal.route('/calendar/modify_event_state', methods=['POST'])
@login_required
def modify_event_state():
    try:
        state = int(request.form.get("state"))
        e_id = request.form.get("id")
        event_obj = models.Events.query.filter(models.Events.id == e_id).first()
        if event_obj:
            event_obj.is_show = 0 if state == 1 else  1
            db.session.commit()
            return jsonify({"success":"ok"})
    except Exception as e :
        db.session.rollback()
        current_app.logger.error(e)
        return render_template("404.html")

