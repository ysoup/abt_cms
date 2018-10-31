import json
import os, sys
# 导入蓝图
from . import ft
from app import models
from cms_server import db
from flask_login import login_required
from ..utils.Pagination import Pagination
from flask import render_template, jsonify, request, current_app, make_response
from .. import models
from app.new_flash.hadoop_service import upload_coin_logo_hdfs

C2C = 1001    # coin to coin
C2P = 1002    # coin to person
C2O = 1003    # coin to organization
P2P = 2001    # person to person
P2O = 2002    # person to organization
O2O = 3001    # organization to organization

SCORE = 1
BASE_PIC_URL = '/static/pic'
BASE_PIC = os.path.join(sys.path[0],"app","static", "pic")


@ft.route("/f10/coin_category_list")
@login_required
def coin_category_list():
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(models.CoinBaseInfo.id,
                                      models.CoinBaseInfo.code,
                                      models.CoinBaseInfo.chinese_name,
                                      models.CoinBaseInfo.english_name,
                                      models.CoinBaseInfo.is_available).paginate(page, per_page=20, error_out=False)
    data = pagination.items
    return render_template("f10/coin_category_list.html", data = data, pagination = pagination)


@ft.route("/f10/modify_coin_state", methods=['POST'])
@login_required
def modify_coin_state():
    try:
        coin_obj = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == request.form.get("id")).first_or_404()
        flag = request.form.get("flag")

        if flag == "0":
            coin_obj.is_available = 1
            db.session.commit()
            return jsonify({'status':'ok', "msg":"展示成功！"})
        elif flag == "1":
            coin_obj.is_available = 0
            db.session.commit()
            return jsonify({"status":'ok', "msg":"取消展示成功"})
        else:
            return jsonify({"status":'failed', "msg":'数据有误，请重新操作！'})
    except Exception as e :
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify({'status':'failed', "msg":'修改状态失败，请重试'})


# 获取预览
@ft.route('/get_log_url', methods=['POST'])
@login_required
def get_log_url():
    if request.method == 'POST':
        try:
            import time
            uu = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            file_obj = request.files.get('file')
            base_pic = BASE_PIC + "/" + uu + (file_obj.filename).replace(" ", "")
            base_pic_url = BASE_PIC_URL + "/" + uu + (file_obj.filename).replace(" ", "")
            with open(base_pic, 'wb') as f:
                for i in file_obj:
                    f.write(i)
            return jsonify({'success': 'ok', 'img_url': base_pic, "base_pic_url": base_pic_url})
        except Exception as e:
            current_app.logger.error(e)
        return jsonify({'failed': 'ok'})


@ft.route('/f10/modify_coin_info', methods=["GET", "POST"])
@login_required
def modify_coin_info():
    if request.method == 'GET':
        base_obj = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == request.args.get("id")).first()
        git_obj = models.CoinGithubData.query.filter(models.CoinGithubData.coin_id == request.args.get("id")).first()
        social_obj = models.CoinSocialData.query.filter(models.CoinSocialData.coin_id == request.args.get("id")).first()
        roadmap_obj_list = models.CoinRoadmap.query.filter(models.CoinRoadmap.coin_id == request.args.get("id")).all()
        hold_addr_obj = models.CoinHoldingAddressStatis.query.filter(models.CoinHoldingAddressStatis.coin_id == request.args.get("id")).first()
        cash_flow_obj = models.CoinCashFlow.query.filter(models.CoinCashFlow.coin_id == request.args.get("id")).first()
        coin_board_list = models.CoinBoardInfo.query.all()

        or_per_list = models.ObjectRelations.query.filter(models.ObjectRelations.type == C2P, models.ObjectRelations.obj1_id == base_obj.id).all()
        or_coin_list = models.ObjectRelations.query.filter(models.ObjectRelations.type == C2C, models.ObjectRelations.obj1_id == base_obj.id).all()
        or_organ_list = models.ObjectRelations.query.filter(models.ObjectRelations.type == C2O, models.ObjectRelations.obj1_id == base_obj.id).all()
        team_list = []
        for or_per_obj in or_per_list:
            per_dict = {}
            per_obj = models.PersonInfo.query.filter(models.PersonInfo.id == or_per_obj.obj2_id).first()
            # per_dict["per_name"], per_dict["per_intro"], per_dict["desc"] = per_obj.name, per_obj.intro, or_per_obj.desc if per_obj else ""
            if per_obj:
                per_dict["per_id"], per_dict["per_name"], per_dict["per_intro"], per_dict["desc"], per_dict['or_id'] = per_obj.id, per_obj.name, per_obj.intro, or_per_obj.desc, or_per_obj.id
            else:
                continue
            team_list.append(per_dict)

        # 知识图谱相关
        base_coin_list = db.session.query(models.CoinBaseInfo.id, models.CoinBaseInfo.code).limit(100).all()
        base_organ_list = db.session.query(models.OrganizationInfo.id, models.OrganizationInfo.name).all()
        base_person_list = db.session.query(models.PersonInfo.id, models.PersonInfo.name).all()


        coin_list = []
        for or_coin_obj in or_coin_list:
            coin_obj = db.session.query(models.CoinBaseInfo.code, models.CoinBaseInfo.id).filter(models.CoinBaseInfo.id == or_coin_obj.obj2_id).first()
            if coin_obj:
                rela_coin_obj = db.session.query(models.ObjectRelations.desc).filter(models.ObjectRelations.type==C2C, models.ObjectRelations.obj1_id==base_obj.id, models.ObjectRelations.obj2_id==coin_obj.id).first()
                coin_list.append({'coin_id':coin_obj.id, "coin_code":coin_obj.code, "desc":rela_coin_obj.desc} if coin_obj else "")
        # print(coin_list) # [{'coin_id': 589, 'coin_code': 'SPC', 'desc': '相同团队'}, {'coin_id': 4, 'coin_code': 'BCH', 'desc': ''}, {'coin_id': 2211, 'coin_code': 'B2X', 'desc': ''}, {'coin_id': 3, 'coin_code': 'XRP', 'desc': ''}, {'coin_id': 1293, 'coin_code': 'XPD', 'desc': ''}, {'coin_id': 10, 'coin_code': 'USDT', 'desc': ''}]


        organ_list = []
        for or_organ_obj in or_organ_list:
            organ_obj = db.session.query(models.OrganizationInfo.id, models.OrganizationInfo.name).filter(models.OrganizationInfo.id == or_organ_obj.obj2_id).first()
            if organ_obj:
                rela_organ_obj = db.session.query(models.ObjectRelations.desc).filter(models.ObjectRelations.type==C2O, models.ObjectRelations.obj1_id==base_obj.id, models.ObjectRelations.obj2_id==organ_obj.id).first()
                organ_list.append({"organ_id":organ_obj.id, "organ_name":organ_obj.name, "desc":rela_organ_obj.desc} if organ_obj else "")

        boards_list = list(map(int, base_obj.boards.split(","))) if base_obj.boards else []

        return render_template("f10/modify_coin_info.html", base_obj=base_obj, git_obj=git_obj, social_obj=social_obj, roadmap_obj_list=roadmap_obj_list,
                               hold_addr_obj=hold_addr_obj, cash_flow_obj=cash_flow_obj, coin_board_list=coin_board_list, boards_list=boards_list,
                               team_list=team_list, coin_list=coin_list, organ_list=organ_list, base_coin_list=base_coin_list, base_person_list=base_person_list, base_organ_list=base_organ_list)

    elif request.method == 'POST':
        try:
            id = request.form.get("id", type=int)
            delete_pers_id = request.form.get("delete_pers_id")
            road_map_data = request.form.get("roadmap_data")
            logo_img = request.form.get("log_img")
            img_url = request.form.get("img_url")
            base_coin_data = request.form.get("base_coin_data")
            base_person_data = request.form.get("base_person_data")
            base_organ_data = request.form.get("base_organ_data")

            coin_obj = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == id).first()

            if img_url:
                filename = logo_img.replace("/static/pic/", "")
                logo_img = upload_coin_logo_hdfs(filename, img_url)
                if not logo_img:
                    return jsonify({"status":"failed", "msg":'获取Hadoop图片失败，请重试！'})

            if coin_obj:
                # delete C2C relations
                try:
                    models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id==coin_obj.id, models.ObjectRelations.type==C2C).delete()
                    # db.session.commit()
                except Exception as e :
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed',"msg":"操作关联币种ID时出现问题，请重试"})
                # add C2C relations
                try:
                    for base_coin in json.loads(base_coin_data):
                        relation_c2c = models.ObjectRelations(obj1_id=coin_obj.id, obj2_id=base_coin['coin_id'], desc=base_coin.get("coin_desc"), score=SCORE, type=C2C)
                        db.session.add(relation_c2c)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed',"msg":"写入关联币种关系时出现问题，请重试"})

                # delete C2P relations
                try:
                    models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id==coin_obj.id, models.ObjectRelations.type==C2P).delete()
                except Exception as e :
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed',"msg":"操作关联人物ID时出现问题，请重试"})
                # add C2P relations
                try:
                    for base_person in json.loads(base_person_data):
                        relation_c2p = models.ObjectRelations(obj1_id=coin_obj.id, obj2_id=base_person.get("person_id"), type=C2P, desc=base_person.get("person_desc"), score=SCORE)
                        db.session.add(relation_c2p)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed',"msg":"写入关联人物关系时出现问题，请重试"})

                # delete C2O relations
                try:
                    models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id==coin_obj.id, models.ObjectRelations.type==C2O).delete()
                except Exception as e :
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed',"msg":"操作关联机构时出现问题，请重试"})
                # add C2O relations
                try:
                    for base_organ in json.loads(base_organ_data):
                        relation_c2o = models.ObjectRelations(obj1_id=coin_obj.id, obj2_id=base_organ.get("organ_id"), type=C2O, desc=base_organ.get("organ_desc"), score=SCORE)
                        db.session.add(relation_c2o)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed',"msg":"写入关联机构关系时出现问题，请重试"})

                # delete C2P relations
                try:
                    for delete_per_id in json.loads(delete_pers_id):
                        delete_per_obj = models.ObjectRelations.query.filter(models.ObjectRelations.type==C2P, models.ObjectRelations.obj1_id==coin_obj.id, models.ObjectRelations.obj2_id==delete_per_id).first_or_404()
                        db.session.delete(delete_per_obj)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(e)
                    return jsonify({"status":'failed',"msg":"删除关联人物时出现问题，请重试"})

                # reset relation road_map_info
                try:
                    models.CoinRoadmap.query.filter(models.CoinRoadmap.coin_id == coin_obj.id).delete()
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed',"msg":"RoadMap操作出现问题，请重试"})
                try:
                    """
                    json.loads(road_map_data)
                    [
                        {'coin_start_time': '100', 'work_time_desc': '2014/8/1', 'work_item': '恒星币正式启动'}, 
                        {'coin_start_time': '200', 'work_time_desc': '2015/5/15', 'work_item': 'Jed McCaleb谈论恒星基金会的新共识协议'}, 
                        {'coin_start_time': '300', 'work_time_desc': '2016/12/6', 'work_item': '菲律宾正式接入恒星轨道'}, 
                        {'coin_start_time': '400', 'work_time_desc': '2017/10/16', 'work_item': 'IBM与恒星达成战略合作'}
                    ]
                    """
                    for road_map in json.loads(road_map_data):
                        coin_map_obj = models.CoinRoadmap(coin_id = coin_obj.id, start_time=road_map.get("coin_start_time"), work_time_desc=road_map.get("work_time_desc"), work_item=road_map.get("work_item"))
                        db.session.add(coin_map_obj)
                    db.session.commit()
                except Exception as e :
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed', "msg":'RoadMap写入出现问题，请重试'})

            intro = request.form.get("intro", "")
            chinese_name = request.form.get("chinese_name", "")
            english_name = request.form.get("english_name", "")
            code = request.form.get("code", "")
            publish_time = request.form.get("publish_time") if request.form.get("publish_time") else None
            max_supply = request.form.get("max_supply")
            if max_supply == "None":
                max_supply = 0
            shelf_num = request.form.get("shelf_num", "")
            algorithm = request.form.get("algorithm", "")
            proof_type = request.form.get("proof_type", "")

            website_url = request.form.get("website_url", "")
            wallet_url = request.form.get("wallet_url", "")
            forum_urls = request.form.get("forum_urls", "")
            wp_url = request.form.get("wp_url", "")
            be_urls = request.form.get("be_urls", "")
            github_url = request.form.get("github_url", "")
            reddit_url = request.form.get("reddit_url", "")
            twitter_url = request.form.get("twitter_url", "")
            facebook_url = request.form.get("facebook_url", "")

            ico_plan = request.form.get("ico_plan", "")
            ico_cost =request.form.get("ico_cost", "")
            capital = request.form.get("capital", "")
            ico_time = request.form.get("ico_time", "")

            coin_tags = request.form.get("coin_tags", "")
            board_id_str = ','.join(json.loads(request.form.get("board_id_list","")))


            if coin_obj:
                coin_obj.intro = intro
                coin_obj.code = code
                coin_obj.english_name = english_name
                coin_obj.chinese_name = chinese_name
                coin_obj.logo_img =  logo_img
                coin_obj.shelf_exchange_num = shelf_num
                coin_obj.algorithm = algorithm
                coin_obj.publish_time = publish_time
                coin_obj.max_supply = max_supply
                coin_obj.proof_type = proof_type
                coin_obj.website_url = website_url
                coin_obj.wallet_url = wallet_url
                coin_obj.forum_url = forum_urls
                coin_obj.white_paper = wp_url
                coin_obj.block_explorer_urls = be_urls
                coin_obj.github_url = github_url
                coin_obj.reddit_url = reddit_url
                coin_obj.twitter_url = twitter_url
                coin_obj.facebook_url = facebook_url
                coin_obj.ico_plan = ico_plan
                coin_obj.ico_cost = ico_cost
                coin_obj.ico_capital = capital
                coin_obj.ico_time = ico_time

                coin_obj.tags = coin_tags
                coin_obj.boards = board_id_str

            db.session.commit()
            if img_url:
                os.remove(img_url)
            return jsonify({"status":'ok', 'msg':'币种信息修改成功'})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify({"status":'failed', 'msg':'修改失败，请重试'})


@ft.route("/f10/concept_board_manage", methods=['GET', 'POST'])
@login_required
def concept_board_manage():
    if request.method == "GET":
        # all board
        coin_dict = {}
        boards_list = models.CoinBoardInfo.query.all()
        pager_obj = Pagination(request.args.get('page', 1), len(boards_list), request.path, request.args, per_page_count=50)
        data_list = boards_list[pager_obj.start:pager_obj.end]
        html = pager_obj.page_html()
        # all coin_obj
        for coin_obj in models.CoinBaseInfo.query.all():
            if coin_obj.boards:
                coin_board_list = list(map(int, coin_obj.boards.split(",")))
                for board_obj in boards_list:
                    l = []
                    if board_obj.id in coin_board_list:
                        if coin_dict.get(board_obj.id):
                            coin_dict[board_obj.id].append(coin_obj.chinese_name)
                        else:
                            l.append(coin_obj.chinese_name)
                            coin_dict[board_obj.id] = l
        return render_template("f10/concept_board_manage.html", data = data_list, coin_dict = coin_dict, html=html)


@ft.route('/f10/modify_board', methods=["GET", "POST"])
@login_required
def modify_board():
    if request.method == 'GET':
        board_obj = models.CoinBoardInfo.query.filter(models.CoinBoardInfo.id == request.args.get("id", type=int)).first()
        return render_template("f10/modify_board.html", data = board_obj)
    else:
        try:
            board_name = request.form.get("board_name")
            board_obj = models.CoinBoardInfo.query.filter(models.CoinBoardInfo.id == request.form.get("id")).first()
            board_obj.name = board_name
            db.session.commit()
            return jsonify({"status":'ok', 'msg':'修改成功'})

        except Exception as e :
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify({"status":'failed', 'msg':'修改失败，请重试'})


@ft.route('/f10/person_organ_manage', methods=['GET', "POST"])
@login_required
def person_organ_manage():
    if request.method == 'GET':
        person_list = models.PersonInfo.query.all()
        organ_list = models.OrganizationInfo.query.all()
        coin_data = {}
        for person in person_list:
            relation_obj_list = models.ObjectRelations.query.filter(models.ObjectRelations.type == C2P, models.ObjectRelations.obj2_id == person.id).all() if person else []
            coin_list = []
            for relation_obj in relation_obj_list:
                if relation_obj:
                    coin_obj = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == relation_obj.obj1_id).first() if models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == relation_obj.obj1_id).first() else None
                    coin_list.append(coin_obj.code)
            coin_data[person.id] = coin_list

        return render_template("f10/person_organ_manage.html", person_list = person_list, organ_list = organ_list, coin_data = coin_data)


@ft.route('/f10/modify_person_info', methods=['GET', "POST"])
@login_required
def modify_person_info():
    if request.method == 'GET':
        try:
            person_obj = models.PersonInfo.query.filter(models.PersonInfo.id == request.args.get('id')).first()
            if person_obj:
                coin_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.type == C2P, models.ObjectRelations.obj2_id == person_obj.id, ).all()
                p_coin_list = []
                for relation_obj in coin_relation_list:
                    p_coin_list.append(models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == relation_obj.obj1_id).first().code)

                organ_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.type == P2O, models.ObjectRelations.obj1_id == person_obj.id, ).all()

                p_organ_list = []
                for relation_obj in organ_relation_list:
                    p_organ_list.append(models.OrganizationInfo.query.filter(models.OrganizationInfo.id == relation_obj.obj2_id).first().name)

                return render_template("f10/modify_person_info.html", person_obj = person_obj, p_coin_list = p_coin_list, p_organ_list=p_organ_list)
        except Exception as e:
            current_app.logger.error(e)
            return render_template('404.html')
    elif request.method  == 'POST':
        try :
            id = request.form.get('id')
            name = request.form.get("name")
            intro = request.form.get("intro")
            person_obj = models.PersonInfo.query.filter(models.PersonInfo.id == id).first()
            if person_obj:
                person_obj.name = name
                person_obj.intro = intro
                db.session.commit()
                return jsonify({"status":"ok", "msg":"修改成功"})
        except Exception as e :
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify({"status":'failed', "msg":'修改失败，请重试！'})


@ft.route('/f10/modify_organ_info', methods=['GET', "POST"])
@login_required
def modify_organ_info():
    if request.method == 'GET':
        try:
            organ_obj = models.OrganizationInfo.query.filter(models.OrganizationInfo.id == request.args.get('id')).first()
            if organ_obj:
                coin_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.type == C2O, models.ObjectRelations.obj2_id == organ_obj.id, ).all()
                organ_coin_list = []
                for relation_obj in coin_relation_list:
                    organ_coin_list.append(models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == relation_obj.obj1_id).first().code)

                person_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.type == P2O, models.ObjectRelations.obj2_id == organ_obj.id, ).all()
                organ_person_list = []
                for relation_obj in person_relation_list:
                    organ_person_list.append(models.PersonInfo.query.filter(models.PersonInfo.id == relation_obj.obj1_id).first().name)

                return render_template("f10/modify_organ_info.html", organ_obj = organ_obj, organ_coin_list = organ_coin_list, organ_person_list=organ_person_list)
        except Exception as e :
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try :
            id = request.form.get('id')
            name = request.form.get("name")
            intro = request.form.get("intro")
            organ_obj = models.OrganizationInfo.query.filter(models.OrganizationInfo.id == id).first()
            if organ_obj:
                organ_obj.name = name
                organ_obj.intro = intro
                db.session.commit()
                return jsonify({"status":"ok", "msg":"修改成功"})
        except Exception as e :
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify({"status":'failed', "msg":'修改失败，请重试！'})


@ft.route("/f10/add_person", methods=['GET', 'POST'])
@login_required
def add_person():
    if request.method == 'GET':
        try:
            coin_list = db.session.query(models.CoinBaseInfo.id, models.CoinBaseInfo.code).all()
            organ_list = db.session.query(models.OrganizationInfo.id, models.OrganizationInfo.name).all()
            return render_template("f10/add_person.html", coin_list=coin_list, organ_list=organ_list)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            name = request.form.get("person_name")
            face_img = request.form.get("face_img", "")
            intro = request.form.get("person_intro", "")
            person_obj = models.PersonInfo(name=name, intro=intro, face_img=face_img)
            db.session.add(person_obj)
            db.session.commit()

            if person_obj.id:
                data_dict = json.loads(request.form.get("data_dict"))
                coin_dict = data_dict.get("coin")

                try:
                    for k,v in coin_dict.items():
                        o2p_obj = models.ObjectRelations(obj1_id=k, obj2_id=person_obj.id, type=C2P, desc=v, score=SCORE)
                        db.session.add(o2p_obj)
                except Exception as  e:
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed', "msg":"建立人物与币种关系时，未成功！请重试"})

                organ_dict = data_dict.get("organ")
                try:
                    for k,v in organ_dict.items():
                        p2o_obj = models.ObjectRelations(obj1_id=person_obj.id, obj2_id=k, type=P2O, desc=v, score=SCORE)
                        db.session.add(p2o_obj)
                except Exception as  e:
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({'status':"failed", "msg":"建立人物与机构关系时，未成功！请重试"})

                db.session.commit()
                return jsonify({"status":"ok", "msg":"新增成功"})
            else:
                db.session.rollback()
                return jsonify({"status":"failed", "msg":"人物未添加成功"})

        except Exception as e :
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify({"status":'failed', "msg":"添加失败，请重试"})


@ft.route("/f10/add_organ", methods=['GET', 'POST'])
@login_required
def add_organ():
    if request.method == 'GET':
        try:
            coin_list = db.session.query(models.CoinBaseInfo.id, models.CoinBaseInfo.code).all()
            person_list = db.session.query(models.PersonInfo.id, models.PersonInfo.name).all()
            return render_template("f10/add_organ.html", coin_list=coin_list, person_list=person_list)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            name = request.form.get("organ_name")
            intro = request.form.get("organ_intro", "")
            organ_obj = models.OrganizationInfo(name=name, intro=intro)
            db.session.add(organ_obj)
            db.session.commit()

            if organ_obj.id:
                data_dict = json.loads(request.form.get("data_dict"))
                coin_dict = data_dict.get("coin")
                try:
                    for k,v in coin_dict.items():
                        c2o_obj = models.ObjectRelations(obj1_id=k, obj2_id=organ_obj.id, type=C2O, desc=v, score=SCORE)
                        db.session.add(c2o_obj)
                except Exception as  e:
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({"status":'failed', "msg":"建立人物与机构关系时，未成功！请重试"})

                person_dict = data_dict.get("person")
                try:
                    for k,v in person_dict.items():
                        p2o_obj = models.ObjectRelations(obj2_id=organ_obj.id, obj1_id=k, type=P2O, desc=v, score=SCORE)
                        db.session.add(p2o_obj)
                except Exception as  e:
                    db.session.rollback()
                    current_app.logger.error(e)
                    return jsonify({'status':"failed", "msg":"建立人物与机构关系时，未成功！请重试"})

                db.session.commit()
                return jsonify({"status":"ok", "msg":"新增成功"})
            else:
                db.session.rollback()
                return jsonify({"status":"failed", "msg":"机构添加失败"})

        except Exception as e :
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify({"status":'failed', "msg":"添加失败，请重试"})

@ft.route("/f10/relation_manage", methods=['GET','POST'])
@login_required
def relation_manage():
    if request.method == 'GET':
        page = request.args.get("page", 0, int)
        select_id = request.args.get("select_id", 0, int)
        if select_id == 1: # P2P
            data_list = []
            pagination = db.session.query(models.PersonInfo.id, models.PersonInfo.name).paginate(page, per_page=50,error_out=False)
            person_list = pagination.items
            for person_obj in person_list:
                data = {}
                person_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id == person_obj.id, models.ObjectRelations.type == P2P).all()
                data['id'] = person_obj.id
                data['arg1'] = person_obj.name
                l = []
                for person_relation_obj in person_relation_list:
                    person1_obj = models.PersonInfo.query.filter(models.PersonInfo.id == person_relation_obj.obj2_id).first()
                    if not person1_obj:
                        continue
                    data[person1_obj.name] = person_relation_obj.desc
                    l.append(person1_obj.name)
                data["arg2"] = l
                data_list.append(data)

        elif select_id == 2:  # P2O
            data_list = []
            pagination = db.session.query(models.PersonInfo.id, models.PersonInfo.name).paginate(page, per_page=50,error_out=False)
            person_list = pagination.items
            for person_obj in person_list:
                data = {}
                organ_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id == person_obj.id, models.ObjectRelations.type == P2O).all()
                data['id'] = person_obj.id
                data['arg1'] = person_obj.name
                l = []
                for organ_relation_obj in organ_relation_list:
                    organ_obj = models.OrganizationInfo.query.filter(models.OrganizationInfo.id == organ_relation_obj.obj2_id).first()
                    if not organ_obj:
                        continue
                    data[organ_obj.name] = organ_relation_obj.desc
                    l.append(organ_obj.name)
                data["arg2"] = l
                data_list.append(data)

        elif select_id == 3:  # C2C
            data_list = []
            pagination = db.session.query(models.CoinBaseInfo.id, models.CoinBaseInfo.code).paginate(page, per_page=50, error_out=False)
            coin_list = pagination.items
            for coin_obj in coin_list:
                data = {}
                coin_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id == coin_obj.id,models.ObjectRelations.type == C2C).all()
                data['id'] = coin_obj.id
                data['arg1'] = coin_obj.code
                l = []
                for coin_relation_obj in coin_relation_list:
                    coin1_obj = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == coin_relation_obj.obj2_id).first()
                    if not coin1_obj:
                        continue
                    data[coin1_obj.code] = coin_relation_obj.desc
                    l.append(coin1_obj.code)
                data["arg2"] = l
                data_list.append(data)

        elif select_id == 4:  # C2P
            data_list = []
            pagination = db.session.query(models.CoinBaseInfo.id, models.CoinBaseInfo.code).paginate(page, per_page=50,error_out=False)
            coin_list = pagination.items
            for coin_obj in coin_list:
                data = {}
                person_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id == coin_obj.id,models.ObjectRelations.type == C2P).all()
                data['id'] = coin_obj.id
                data['arg1'] = coin_obj.code
                l = []
                for person_relation_obj in person_relation_list:
                    person_obj = models.PersonInfo.query.filter(models.PersonInfo.id == person_relation_obj.obj2_id).first()
                    if not person_obj:
                        continue
                    data[person_obj.name] = person_relation_obj.desc
                    l.append(person_obj.name)
                data["arg2"] = l
                data_list.append(data)

        elif select_id == 5:  # C2O
            data_list = []
            pagination = db.session.query(models.CoinBaseInfo.id, models.CoinBaseInfo.code).paginate(page, per_page=50,error_out=False)
            coin_list = pagination.items
            for coin_obj in coin_list:
                data = {}
                organ_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id == coin_obj.id, models.ObjectRelations.type == C2O).all()
                data['id'] = coin_obj.id
                data['arg1'] = coin_obj.code
                l = []
                for organ_relation_obj in organ_relation_list:
                    organ_obj = models.OrganizationInfo.query.filter(models.OrganizationInfo.id == organ_relation_obj.obj2_id).first()
                    if not organ_obj:
                        continue
                    data[organ_obj.name] = organ_relation_obj.desc
                    l.append(organ_obj.name)
                data["arg2"] = l
                data_list.append(data)

        elif select_id == 6:  # O2O
            data_list = []
            pagination = db.session.query(models.OrganizationInfo.id, models.OrganizationInfo.name).paginate(page, per_page=50,error_out=False)
            organ_list = pagination.items
            for organ_obj in organ_list:
                data = {}
                organ_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj1_id == organ_obj.id,models.ObjectRelations.type == O2O).all()
                data['id'] = organ_obj.id
                data['arg1'] = organ_obj.name
                l = []
                for organ_relation_obj in organ_relation_list:
                    organ1_obj = models.OrganizationInfo.query.filter(models.OrganizationInfo.id == organ_relation_obj.obj2_id).first()
                    if not organ1_obj:
                        continue
                    data[organ1_obj.name] = organ_relation_obj.desc
                    l.append(organ1_obj.name)
                data["arg2"] = l
                data_list.append(data)

        elif select_id == 7:  # O2P
            data_list = []
            pagination = db.session.query(models.OrganizationInfo.id, models.OrganizationInfo.name).paginate(page, per_page=50, error_out=False)
            organ_list = pagination.items
            for organ_obj in organ_list:
                data = {}
                organ_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj2_id == organ_obj.id, models.ObjectRelations.type == P2O).all()
                data['id'] = organ_obj.id
                data['arg1'] = organ_obj.name
                l = []
                for organ_relation_obj in organ_relation_list:
                    person_obj = models.PersonInfo.query.filter(models.PersonInfo.id == organ_relation_obj.obj1_id).first()
                    if not person_obj:
                        continue
                    data[person_obj.name] = organ_relation_obj.desc
                    l.append(person_obj.name)
                data["arg2"] = l
                data_list.append(data)

        elif select_id == 8:  # O2C
            data_list = []
            pagination = db.session.query(models.OrganizationInfo.id, models.OrganizationInfo.name).paginate(page, per_page=50, error_out=False)
            organ_list = pagination.items
            for organ_obj in organ_list:
                data = {}
                organ_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj2_id == organ_obj.id, models.ObjectRelations.type == C2O).all()
                data['id'] = organ_obj.id
                data['arg1'] = organ_obj.name
                l = []
                for organ_relation_obj in organ_relation_list:
                    coin_obj = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == organ_relation_obj.obj1_id).first()
                    if not coin_obj:
                        continue
                    data[coin_obj.code] = organ_relation_obj.desc
                    l.append(coin_obj.code)
                data["arg2"] = l
                data_list.append(data)

        # else:
        #     person_list = db.session.query(models.PersonInfo.id, models.PersonInfo.name).all()
        #     for person_obj in person_list:
        #         data = {}
        #         coin_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj2_id == person_obj.id,models.ObjectRelations.type == C2P).all()
        #         data['id'] = person_obj.id
        #         data['arg1'] = person_obj.name
        #         l = []
        #         for coin_relation_obj in coin_relation_list:
        #             coin_code = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == coin_relation_obj.obj1_id).first()
        #             data[coin_code.code] = coin_relation_obj.desc
        #             l.append(coin_code.code)
        #         data["arg2"] = l
        #         """
        #         [
        #             {
        #                 'id': 1,
        #                 'arg1': 'Jeff Garzik',
        #                 'BTC': '首席科学家',
        #                 'ETH': '首席策略官',
        #                 'arg2': ['BTC', 'ETH']
        #             },
        #
        #             {'id': 2, 'arg1': 'Matthew Roszak', 'arg2': []},
        #             {'id': 3, 'arg1': 'Wilson Choi', 'BTC': '首席运营官', 'arg2': ['BTC']}
        #         ]
        #
        #         """
        #         data_list.append(data)
        else: # P2C
            data_list = []
            pagination = db.session.query(models.PersonInfo.id, models.PersonInfo.name).paginate(page, per_page=50, error_out=False)
            person_list = pagination.items
            for person_obj in person_list:
                data = {}
                coin_relation_list = models.ObjectRelations.query.filter(models.ObjectRelations.obj2_id == person_obj.id,models.ObjectRelations.type == C2P).all()
                data['id'] = person_obj.id
                data['arg1'] = person_obj.name
                l = []
                for coin_relation_obj in coin_relation_list:
                    coin_obj = models.CoinBaseInfo.query.filter(models.CoinBaseInfo.id == coin_relation_obj.obj1_id).first()
                    if not coin_obj:
                        continue
                    data[coin_obj.code] = coin_relation_obj.desc
                    l.append(coin_obj.code)
                data["arg2"] = l
                """
                [
                    {
                        'id': 1,
                        'arg1': 'Jeff Garzik',
                        'BTC': '首席科学家',
                        'ETH': '首席策略官',
                        'arg2': ['BTC', 'ETH']
                    },
    
                    {'id': 2, 'arg1': 'Matthew Roszak', 'arg2': []},
                    {'id': 3, 'arg1': 'Wilson Choi', 'BTC': '首席运营官', 'arg2': ['BTC']}
                ]
    
                """
                data_list.append(data)

        return render_template("f10/relation_manage.html", data=data_list, pagination=pagination)


@ft.route("/f10/add_relation", methods=['GET','POST'])
@login_required
def add_relation():
    if request.method == 'GET':
        return render_template("f10/add_relation.html")
    elif request.method == 'POST':
        try:
            obj1 = request.form.get("obj1", type=int)
            obj2 = request.form.get("obj2", type=int)
            obj1_id = request.form.get("obj1_id", type=int)
            obj2_id = request.form.get("obj2_id", type=int)
            desc = request.form.get("relation_intro", "")
            if obj1 == 1:  # person
                if obj2 == 1:
                    p2p_obj = models.ObjectRelations(obj1_id=obj1_id, obj2_id=obj2_id, type=P2P, desc=desc, score=SCORE)
                    db.session.add(p2p_obj)
                elif obj2 == 2:
                    p2c_obj = models.ObjectRelations(obj1_id=obj2_id, obj2_id=obj1_id, type=C2P, desc=desc, score=SCORE)
                    db.session.add(p2c_obj)
                elif obj2 == 3:
                    p2o_obj = models.ObjectRelations(obj1_id=obj1_id, obj2_id=obj2_id, type=P2O, desc=desc, score=SCORE)
                    db.session.add(p2o_obj)
                else:
                    return jsonify({"status": 'false', "msg": "非正确选项，请重试person！！！"})
                db.session.commit()
                return jsonify({"status": "ok", "msg": "关联关系添加成功！"})
            elif obj1 == 2:  # coin
                if obj2 == 1:
                    c2p_obj = models.ObjectRelations(obj1_id=obj1_id, obj2_id=obj2_id, type=C2P, desc=desc, score=SCORE)
                    db.session.add(c2p_obj)
                elif obj2 == 2:
                    c2c_obj = models.ObjectRelations(obj1_id=obj1_id, obj2_id=obj2_id, type=C2C, desc=desc, score=SCORE)
                    db.session.add(c2c_obj)
                elif obj2 == 3:
                    c2o_obj = models.ObjectRelations(obj1_id=obj1_id, obj2_id=obj2_id, type=C2O, desc=desc, score=SCORE)
                    db.session.add(c2o_obj)
                else:
                    return jsonify({"status": 'false', "msg": "非正确选项，请重试coin！！！"})
                db.session.commit()
                return jsonify({"status": "ok", "msg": "关联关系添加成功！"})
            elif obj1 == 3: # organization
            # else:  # organization
                if obj2 == 1:
                    o2p_obj = models.ObjectRelations(obj1_id=obj2_id, obj2_id=obj1_id, type=P2O, desc=desc, score=SCORE)
                    db.session.add(o2p_obj)
                elif obj2 == 2:
                    o2c_obj = models.ObjectRelations(obj1_id=obj2_id, obj2_id=obj1_id, type=C2O, desc=desc, score=SCORE)
                    db.session.add(o2c_obj)
                elif obj2 == 3:
                    o2o_obj = models.ObjectRelations(obj1_id=obj1_id, obj2_id=obj2_id, type=O2O, desc=desc, score=SCORE)
                    db.session.add(o2o_obj)
                else:
                    return jsonify({"status": 'false', "msg": "非正确选项，请重试organization！！！"})
                db.session.commit()
                return jsonify({"status":"ok", "msg":"关联关系添加成功！"})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify({"status":'false', "msg":"添加关联关系失败，请重试！！！"})


@ft.route('/f10/get_choice_type', methods = ["GET"])
@login_required
def get_choice_type():
    choice_type = request.args.get("choice_type", 1, int)
    if choice_type == 2:
        choice_data = db.session.query(models.CoinBaseInfo.id, models.CoinBaseInfo.code).all()
    elif choice_type == 3:
        choice_data = db.session.query(models.OrganizationInfo.id, models.OrganizationInfo.name).all()
    elif choice_type == 1:
        choice_data = db.session.query(models.PersonInfo.id, models.PersonInfo.name).all()
    else:
        choice_data = -1
    return jsonify({"success":"ok", 'choice_data':choice_data})


from ..utils.sphinxapi3_query_keyword import query_keyword


# 币种关键字搜索
@ft.route('/f10/coin_search_result', methods=['GET'])
@login_required
def coin_search_result():
    try:
        keyword = request.args.get("keyword")
        coin_list = query_keyword("coin_base", keyword, current_app.config['SP_HOST'], current_app.config["SP_PORT"])
        coin_obj_list = []
        for coin_id in coin_list:
            coin_obj = models.CoinBaseInfo.query.filter_by(id=int(coin_id)).first()
            coin_obj_list.append(coin_obj)
        coin_obj_list.sort(key=lambda coin_obj: coin_obj.id)
        pager_obj = Pagination(request.args.get("page", 1), len(coin_obj_list), request.path, request.args,per_page_count = 20)
        data = coin_obj_list[pager_obj.start:pager_obj.end]
        html = pager_obj.page_html()
        return render_template("f10/coin_search_result.html", data=data, html=html, result_count = len(coin_obj_list))
    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")