from . import planet
import json, datetime
from flask import current_app, request, render_template, jsonify
from ..utils.Pagination import Pagination
from common.planet_service import *


####################### 星球相关 ########################
# 所有星球信息
@planet.route("/planet/planet_info", methods=['GET', "POST"])
def planet_info():
    if request.method == "GET":
        try:
            res = json.loads(common_planet_info())
            if res.get("code") != 0:
                current_app.logger.error("planet_info - res.code != 0", res.get('code'))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path, request.args,
                                   per_page_count=10)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet/planet_info.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

    elif request.method == "POST":
        try:
            planet_no = request.form.get("planet_no")
            res = common_delete_planet(planet_no)
            if json.loads(res).get('code') == 0:
                return jsonify({'success': 'ok'})
            return jsonify({'failed': '操作失败，请重试'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 添加星球信息
@planet.route("/planet/add_planet_detail", methods=['GET', "POST"])
def add_planet_detail():
    if request.method == "GET":
        try:
            return render_template("planet/add_planet_detail.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == "POST":
        try:
            discoverytime = request.form.get("discoverytime")
            discovery_time = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") if discoverytime == "" else discoverytime
            number = 0 if request.form.get("number") == "" else request.form.get("number")
            asset_number = 0 if request.form.get("assetnumber") == "" else request.form.get("assetnumber")
            data = {
                'planet_no': request.form.get("planet_no"),
                'name': request.form.get("name", ""),
                'short_name': request.form.get("shortname", ""),
                'type': request.form.get("type", "2"),
                # 'address': request.form.get("address", ""),
                'owner_no': request.form.get("owner_no"),
                'main_asset': request.form.get("mainasset"),
                'is_issued': request.form.get("isissued", "0"),
                'is_delete': request.form.get("is_delete", 0),
                'is_mined': request.form.get("ismined", "0"),
                'number': number,
                'asset_number': asset_number,
                'status': request.form.get("status", "0"),
                'remark': request.form.get("remark", ""),
                'discoverytime': discovery_time,
                'note': request.form.get("note", ""),
                "image_no": request.form.get("image_no", ""),
                "template": request.form.get("template", ""),
                "grade": request.form.get("grade", ""),
                "background": request.form.get("background", "")
            }

            # 调用接口，发送数据POST
            res = json.loads(common_add_planet(data))
            if res.get('code') == 0:
                return jsonify({'code': 0, "msg": res.get("msg")})
            elif res.get("code") == 1:
                return jsonify({"code": 1, "msg": res.get("msg")})
            return jsonify({'failed': '新增失败，请重试'})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 单个星球信息（修改）
@planet.route("/planet/planet_detail", methods=['GET', "POST"])
def modify_planet_detail():
    if request.method == "GET":
        try:
            planet_no = request.args.get("planet_no")
            res = json.loads(common_planet_detail(planet_no))
            if res.get("code") != 0:
                current_app.logger.error("planet_detail - res.code = %s" % res.get("code"))
                return render_template("404.html")
            return render_template("planet/modify_planet_detail.html", data=res.get("data"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == "POST":
        try:
            discoverytime = request.form.get("discoverytime")
            discovery_time = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S") if discoverytime == "" else discoverytime
            number = 0 if request.form.get("number") == "" else request.form.get("number")
            asset_number = 0 if request.form.get("assetnumber") == "" else request.form.get("assetnumber")
            data = {
                'planet_no': request.form.get("planet_no"),
                'name': request.form.get("name", ""),
                'short_name': request.form.get("shortname", ""),
                'type': request.form.get("type", "1"),
                'address': request.form.get("address", ""),
                'owner_no': request.form.get("owner_no"),
                'main_asset': request.form.get("mainasset"),
                'is_issued': request.form.get("isissued", "0"),
                'is_delete': request.form.get("is_delete", 0),
                'is_mined': request.form.get("ismined", "0"),
                'number': number,
                'asset_number': asset_number,
                'status': request.form.get("status", "0"),
                'remark': request.form.get("remark", ""),
                'discoverytime': discovery_time,
                'note': request.form.get("note", ""),
                "image_no": request.form.get("image_no", ""),
                "template": request.form.get("template", ""),
                "grade": request.form.get("grade", ""),
                "background": request.form.get("background", "")
            }

            # 调用接口，发送数据POST
            res = common_modify_planet(request.form.get("planet_no"), data)
            if res.status_code == 200:
                r = json.loads(res.text)
                if r.get('code') == 0:
                    return jsonify({'code': 0, "msg": r.get("msg")})
                elif r.get("code") == 1:
                    return jsonify({"code": 1, "msg": r.get("msg")})
            return jsonify({'failed': "修改失败"})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 星球主信息
@planet.route("/planet/planet_owner")
def planet_owner():
    if request.method == "GET":
        try:
            res = json.loads(common_planet_owner())
            if res.get("code") != 0:
                current_app.logger.error("planet_owner - res.code != 0 ", res.get("code"))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path, request.args,
                                   per_page_count=10)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet/planet_owner.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 编辑星球主信息
@planet.route("/planet/modify_planet_owner", methods=['GET', "POST"])
def modify_planet_owner():
    if request.method == 'GET':
        try:
            sn = request.args.get("sn")
            res = common_modify_planet_owner(sn=sn, flag=True)
            if res.get("code") != 0:
                current_app.logger.error("modify_planet_owner - res.code is %s " % (res.get("code")))
                return render_template("404.html")
            return render_template("planet/modify_planet_owner.html", data=res.get('data'))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            data = request.form.to_dict()
            res = common_modify_planet_owner(data=data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 新增星球主信息
@planet.route("/planet/add_planet_owner", methods=['GET', 'POST'])
def add_planet_owner():
    if request.method == 'GET':
        return render_template("planet/add_planet_owner.html")
    elif request.method == 'POST':
        try:
            data = request.form.to_dict()
            res = common_add_planet_owner(data=data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
        pass


# 星球币信息
@planet.route("/planet/planet_token")
def planet_token():
    if request.method == "GET":
        try:
            res = json.loads(common_planet_token())
            if res.get("code") != 0:
                current_app.logger.error("planet_token - res.code != 0 ", res.get("code"))
                return render_template("404.html")
            data_res = res.get("data")
            select_id = request.args.get("select_id")
            if select_id == str(2):
                data = []
                for info in data_res:
                    if info.get("type") == "2":
                        data.append(info)
            elif select_id == str(1):
                data = []
                for info in data_res:
                    if info.get("type") == "1":
                        data.append(info)
            else:
                data = data_res
            pager_obj = Pagination(request.args.get("page", 1), len(data), request.path, request.args,
                                   per_page_count=10)
            data = data[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet/planet_token.html", data=data, html=html)

        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 编辑星球币
@planet.route("/planet/modify_planet_token", methods=["GET", "POST"])
def modify_planet_token():
    if request.method == 'GET':
        try:
            sn = request.args.get("sn")
            res = common_planet_token_detail(sn=sn, flag=True)
            if res.get("code") != 0:
                current_app.logger.error("modify_planet_token - res.code = %s " % res.get("code"))
                return render_template("404.html")
            return render_template("planet/modify_planet_token_detail.html", data=res.get("info"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == "POST":
        try:
            data = request.form.to_dict()
            if not data.get("mortgage_amount") or data.get("mortgage_amount") == 'None':
                data['mortgage_amount'] = 0

            if not data.get("interest_base") or data.get("interest_base") == 'None':
                data['interest_base'] = 0
            if not data.get("issue_team"):
                data['issue_team'] = 1
            if not data.get("lastterm_interest_date") or data.get("lastterm_interest_date") == 'None':
                data['lastterm_interest_date'] = None
            res = common_planet_token_detail(data=data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 新增PlanetToken
@planet.route("/planet/add_planet_token", methods=["GET", "POST"])
def add_planet_token():
    if request.method == 'GET':
        return render_template("planet/add_planet_token_detail.html")
    elif request.method == 'POST':
        try:
            data = request.form.to_dict()
            if not data.get("mortgage_amount") or data.get("mortgage_amount") == 'None':
                data['mortgage_amount'] = 0
            if not data.get("interest_base") or data.get("interest_base") == 'None':
                data['interest_base'] = 0
            if not data.get("issue_team"):
                data['issue_team'] = 1
            if not data.get("lastterm_interest_date") or data.get("lastterm_interest_date") == 'None':
                data['lastterm_interest_date'] = None
            res = common_add_planet_token(data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


######################## 公告相关 #########################
import os, sys
from PIL import Image

BASE_PIC = os.path.join(sys.path[0], "app", "static", "pic")
BASE_PIC_URL = '/static/pic'
from ..new_flash.hadoop_service import *


# 获取ICON预览
@planet.route('/upload_icon', methods=['POST'])
def upload_icon():
    if request.method == 'POST':
        try:
            import time
            uu = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            file_obj = request.files.get('file')
            fname, fext = os.path.splitext(file_obj.filename)
            base_pic = BASE_PIC + "/pl_icon_" + uu + fext
            base_pic_url = BASE_PIC_URL + "/pl_icon_" + uu + fext
            img = Image.open(file_obj)
            if len(img.split()) == 4:
                # prevent IOError: cannot write mode RGBA as BMP
                r, g, b, a = img.split()
                img = Image.merge("RGBA", (r, g, b, a))
            img.thumbnail((330, 330), Image.ANTIALIAS)
            img.save(base_pic)
            filename = base_pic_url.replace("/static/pic/", '')
            new_img_url = upload_images_hdfs(filename, base_pic)
            if not new_img_url:
                return jsonify({'failed': '上传hadoop失败，请重试！'})
            os.remove(base_pic)
            return jsonify({'success': 'ok', "new_img_url": new_img_url})
        except Exception as e:
            current_app.logger.error(e)
        return jsonify({'failed': 'ok'})


# 公告管理
@planet.route("/planet/notice_info", methods=['GET', 'POST'])
def notice_info():
    if request.method == 'GET':
        try:
            res = common_notice_info()
            if res.get("code") != 0:
                current_app.logger.error("planet_detail - res.code = %s " % res.get("code"))
                return render_template("404.html")
            return render_template("planet/notice_info.html", data=res.get("data"))
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 新增公告
@planet.route("/planet/create_notice", methods=['GET', 'POST'])
def create_notice():
    if request.method == 'GET':
        try:
            return render_template("planet/add_notice.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            data = {
                "type": str(request.form.get("notice_type")),
                "title": request.form.get("notice_title"),
                "summary": request.form.get("notice_summary"),
                "content": request.form.get("notice_content"),
                "url": str(request.form.get("notice_url")),
                "show": str(request.form.get("is_show")),
                "create_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            res = common_create_notice(data)
            if res.get("code") != 0:
                current_app.logger.error("create_notice - POST - res.code = %s" % res.get("code"))
                return jsonify({"status": "failed", "msg": "添加公告失败，请重试！"})
            return jsonify({"status": "success", "msg": "公告新增成功！"})

        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 改变notice状态
@planet.route("/planet/modify_notice_status", methods=['POST'])
def modify_notice_status():
    if request.method == "POST":
        try:
            sn = request.form.get("notice_no")
            data = {"sn": sn}
            res = common_modify_notice_status(data)
            if res.get("code") != 0:
                current_app.logger.error("planet_detail - res.code = %s " % res.get("code"))
                return jsonify({"status": "failed", "msg": res.get("msg")})
            return jsonify({"status": "ok", "msg": res.get("msg")})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


################################## 邀请码 ################################
# 获取邀请码信息
@planet.route("/planet/invite_codes", methods=["GET", "POST"])
def invite_codes():
    if request.method == 'GET':
        try:
            res = common_get_invite_codes()
            if res.get("code") != 0:
                current_app.logger.error("invite_codes - res.code = %s " % res.get("code"))
                return render_template("404.html")
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path, request.args,
                                   per_page_count=20)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet/invite_code.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 编辑邀请码信息
@planet.route("/planet/modify_invite_code", methods=['GET', "POST"])
def modify_invite_code():
    if request.method == 'GET':
        try:
            invite_id = request.args.get("id")
            res = common_modify_invite_code(id=invite_id, flag=True)
            if res.get("code") == 0:
                return render_template("planet/modify_invite_code.html", data=res.get('data'))
            current_app.logger.error("modify_invite_code - GET ERROR!")
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            number1 = request.form.get("number1")
            number = request.form.get("number")
            id = request.form.get("id")
            data = {
                'id' : id,
                "number1" : number1,
                "number" : number
            }
            res = common_modify_invite_code(data=data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 生成邀请码
@planet.route("/planet/generate_invite_code", methods=['GET', "POST"])
def generate_invite_code():
    if request.method == 'GET':
        return render_template("planet/generate_invite_code.html")
    elif request.method == 'POST':
        try:
            number = request.form.get("invite_code_num")
            status = request.form.get("status")
            visibility = request.form.get("is_visibility")

            data = {"number": number, "status": status, "visibility": visibility, "projectno": 9}
            res = common_generate_invitecodes(data)
            if res.get("code") == 0:
                return jsonify({"status": "success"})
            return jsonify({"status": "failed", "msg": "邀请码生成失败，请重试"})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 修改invite status
@planet.route("/planet/modify_invite_status", methods=['POST'])
def modify_invite_status():
    if request.method == 'POST':
        try:
            status = request.form.get("status")
            id = request.form.get("code_id")
            data = {"id": id, "status": status}
            res = common_modify_invite_status(data)
            if res.get("code") == 0:
                return jsonify({"success": "ok"})
            return jsonify({"failed": "Status修改失败，请重试"})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 修改invite visibility
@planet.route("/planet/modify_invite_visibility", methods=['POST'])
def modify_invite_visibility():
    if request.method == 'POST':
        try:
            visibility = request.form.get("visibility")
            id = request.form.get("code_id")
            data = {"id": id, "visibility": visibility}
            res = common_modify_invite_visibility(data)
            if res.get("code") == 0:
                return jsonify({"success": "ok"})
            return jsonify({"failed": "Visibility修改失败，请重试"})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 设置推荐星球
@planet.route('/planet/set_hot_planet', methods=['POST'])
def set_hot_planet():
    if request.method == 'POST':
        try:
            planet_no = request.form.get("planet_no")
            data = {'planet_no': planet_no}
            res = common_set_hot_planet(data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("info")})
            return jsonify({"msg": res.get("info")})

        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


#################### 推荐相关 #######################
# 推荐星球信息
@planet.route("/planet/hot_planets", methods=["GET", 'POST'])
def hot_planets():
    if request.method == 'GET':
        try:
            res = common_get_hot_planets()
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path, request.args,
                                   per_page_count=20)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet/hot_planet_info.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 推荐Token信息
@planet.route("/planet/hot_tokens", methods=['GET', "POST"])
def hot_tokens():
    if request.method == 'GET':
        try:
            res = common_hot_token()
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path, request.args,
                                   per_page_count=20)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet/hot_token_info.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

# 推荐Business信息
@planet.route("/planet/hot_businesses", methods=['GET', "POST"])
def hot_businesses():
    if request.method == 'GET':
        try:
            res = common_hot_businesses()
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path,
                                   request.args,
                                   per_page_count=20)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet/hot_businesses_info.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 编辑推荐Business
@planet.route("/planet/modify_hot_business", methods=["GET", "POST", "PATCH"])
def modify_hot_business():
    if request.method == 'GET':
        try:
            token_no = request.args.get("card_no")
            res = common_modify_hot_business(token_no=token_no, flag=True)
            if res.get("code") == 0:
                return render_template("planet/modify_hot_business_detail.html", data=res.get('data'))
            current_app.logger.error("modify_hot_business - GET ERROR!")
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            max_num = request.form.get("max_num")
            total_amount = request.form.get("total_amount")
            token_no = request.form.get("token_no")
            card_owner = request.form.get("card_owner")
            card_name = request.form.get("card_name")
            card_secret = request.form.get("card_secret")
            card_url = request.form.get("card_url")
            card_img = request.form.get("card_img")
            note = request.form.get("note")
            start_time = request.form.get("start_time")
            end_time = request.form.get("end_time")
            weight = request.form.get("weight", 0, type=int)
            card_worth = request.form.get("card_worth")
            card_desc = request.form.get("card_desc")
            is_delete = request.form.get("is_delete")
            card_remind = request.form.get("card_remind")

            data = {"max_num": max_num, "total_amount": total_amount, "token_no": token_no, "card_owner": card_owner,
                    "card_name": card_name, "card_img": card_img, "note": note, "card_worth": card_worth,
                    "start_time": start_time, "end_time": end_time, "weight": weight, "card_desc": card_desc,
                    "is_delete": is_delete, "card_remind": card_remind, "card_secret": card_secret, "card_url": card_url}
            res = common_modify_hot_business(data=data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 2:
                return jsonify({"msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'PATCH':
        try:
            status = request.form.get("status")
            sn = request.form.get("sn")
            data = {"sn": sn, "status": status}
            res = common_modify_hot_business_status(data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": "状态修改成功"})
            return jsonify({"msg": "状态修改失败，请重试"})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 设置推荐Business
@planet.route('/planet/set_hot_business', methods=["GET", 'POST'])
def set_hot_business():
    if request.method == 'GET':
        try:
            token_no = request.args.get("token_no")
            res = common_set_hot_business(flag=True, token_no=token_no)
            if res.get("code") == 0:
                return render_template("planet/set_hot_business_detail.html", data=res.get("data"))
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("msg"), "code": 1})
            elif res.get("code") == 2:
                return jsonify({"msg": res.get("msg"), "code": 2})
            current_app.logger.error("set_hot_token - GET ERROR!")
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

    # 新增推荐Business
    elif request.method == 'POST':
        try:
            max_num = request.form.get("max_num")
            total_amount = request.form.get("total_amount")
            token_no = request.form.get("token_no")
            card_owner = request.form.get("card_owner")
            card_name = request.form.get("card_name")
            card_img = request.form.get("card_img")
            note = request.form.get("note")
            start_time = request.form.get("start_time")
            end_time = request.form.get("end_time")
            weight = request.form.get("weight", 0, type=int)
            card_worth = request.form.get("card_worth")
            card_desc = request.form.get("card_desc")
            card_remind = request.form.get("remind")
            card_secret = request.form.get("card_secret")
            card_url = request.form.get("card_url")

            data = {"max_num": max_num, "total_amount": total_amount, "token_no": token_no, "card_owner": card_owner,
                    "card_name": card_name, "card_img": card_img, "note": note, "card_worth": card_worth,
                    "start_time": start_time, "end_time": end_time, "weight": weight, "card_desc": card_desc,
                    "card_remind": card_remind, "card_secret": card_secret, "card_url": card_url}

            res = common_set_hot_business(data=data)

            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# DEL推荐星球
@planet.route('/planet/del_hot_planet', methods=['POST'])
def del_hot_planet():
    if request.method == 'POST':
        try:
            planet_no = request.form.get("planet_no")
            data = {"planet_no": planet_no}
            res = common_del_hot_planet(data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            return jsonify({"msg": res.get("info")})

        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 编辑热门星球
@planet.route("/planet/modify_hot_planet", methods=['GET', "POST"])
def modify_hot_planet():
    if request.method == "GET":
        try:
            planet_no = request.args.get("planet_no")
            res = common_get_hot_planet(planet_no=planet_no, flag=True)
            if res.get("code") == 0:
                return render_template("planet/modify_hot_planet_detail.html", data=res.get('data'))
            current_app.logger.error("modify_hot_planet - GET ERROR!")
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            data = {
                'planet_no': request.form.get("planet_no"),
                'weight': request.form.get("weight"),
                'note': request.form.get("note")
            }
            res = common_get_hot_planet(data=data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("msg")})
            return jsonify({"msg": res.get("msg")})

        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 设置推荐Token
@planet.route('/planet/set_hot_token', methods=["GET", 'POST'])
def set_hot_token():
    if request.method == 'GET':
        try:
            token_no = request.args.get("token_no")
            res = common_set_hot_token(flag=True, token_no=token_no)
            if res.get("code") == 0:
                return render_template("planet/set_hot_token_detail.html", data=res.get("data"))
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("msg"), "code": 1})
            elif res.get("code") == 2:
                return jsonify({"msg": res.get("msg"), "code": 2})
            current_app.logger.error("set_hot_token - GET ERROR!")
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")

    # 新增推荐Token
    elif request.method == 'POST':
        try:
            max_num = request.form.get("max_num")
            card_num = request.form.get("card_num")
            token_no = request.form.get("token_no")
            card_owner = request.form.get("card_owner")
            card_name = request.form.get("card_name")
            card_img = request.form.get("card_img")
            note = request.form.get("note")
            start_time = request.form.get("start_time")
            end_time = request.form.get("end_time")
            weight = request.form.get("weight", 0, type=int)
            card_worth = request.form.get("card_worth")
            card_desc = request.form.get("card_desc")
            card_remind = request.form.get("remind")

            data = {"max_num": max_num, "card_num": card_num, "token_no": token_no, "card_owner": card_owner,
                    "card_name": card_name, "card_img": card_img, "note": note, "card_worth": card_worth,
                    "start_time": start_time, "end_time": end_time, "weight": weight, "card_desc": card_desc, "card_remind": card_remind}

            res = common_set_hot_token(data=data)

            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 1:
                return jsonify({"msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 编辑推荐Token
@planet.route("/planet/modify_hot_token", methods=["GET", "POST", "PATCH"])
def modify_hot_token():
    if request.method == 'GET':
        try:
            token_no = request.args.get("card_no")
            res = common_modify_hot_token(token_no=token_no, flag=True)
            if res.get("code") == 0:
                return render_template("planet/modify_hot_token_detail.html", data=res.get('data'))
            current_app.logger.error("modify_hot_token - GET ERROR!")
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            max_num = request.form.get("max_num")
            card_num = request.form.get("card_num")
            token_no = request.form.get("token_no")
            card_owner = request.form.get("card_owner")
            card_name = request.form.get("card_name")
            card_img = request.form.get("card_img")
            note = request.form.get("note")
            start_time = request.form.get("start_time")
            end_time = request.form.get("end_time")
            weight = request.form.get("weight", 0, type=int)
            card_worth = request.form.get("card_worth")
            card_desc = request.form.get("card_desc")
            is_delete = request.form.get("is_delete")
            card_remind = request.form.get("card_remind")

            data = {"max_num": max_num, "card_num": card_num, "token_no": token_no, "card_owner": card_owner,
                    "card_name": card_name, "card_img": card_img, "note": note, "card_worth": card_worth,
                    "start_time": start_time, "end_time": end_time, "weight": weight, "card_desc": card_desc,
                    "is_delete": is_delete, "card_remind": card_remind}
            res = common_modify_hot_token(data=data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": res.get("info")})
            elif res.get("code") == 2:
                return jsonify({"msg": res.get("info")})
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'PATCH':
        try:
            status = request.form.get("status")
            sn = request.form.get("sn")
            data = {"sn": sn, "status": status}
            res = common_modify_hot_token_status(data)
            if res.get("code") == 0:
                return jsonify({"status": "success", "msg": "状态修改成功"})
            return jsonify({"msg": "状态修改失败，请重试"})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 获取卡券详情图片
@planet.route('/upload_hot_card', methods=['POST'])
def upload_hot_card():
    if request.method == 'POST':
        try:
            import time
            uu = time.strftime("%Y%m%d_%H%M%S", time.localtime())
            file_obj = request.files.get('file')
            fname, fext = os.path.splitext(file_obj.filename)
            base_pic = BASE_PIC + "/hot_card_" + uu + fext
            base_pic_url = BASE_PIC_URL + "/hot_card_" + uu + fext
            img = Image.open(file_obj)
            if len(img.split()) == 4:
                # prevent IOError: cannot write mode RGBA as BMP
                r, g, b, a = img.split()
                img = Image.merge("RGBA", (r, g, b, a))
            img.thumbnail((710, 360), Image.ANTIALIAS)
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


################################### 动态相关 ###################################
# 动态信息列表
@planet.route('/news_notification',methods=['GET', 'POST'])
def news_notification():
    if request.method == 'GET':
        try:
            res = common_news_notification()
            pager_obj = Pagination(request.args.get("page", 1), len(res.get("data")), request.path,
                                   request.args,
                                   per_page_count=20)
            data = res.get("data")[pager_obj.start:pager_obj.end]
            html = pager_obj.page_html()
            return render_template("planet/news_notification.html", data=data, html=html)
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 新增动态信息
@planet.route("/create_news_notification", methods=["GET", "POST"])
def create_news_notification():
    if request.method == 'GET':
        return render_template("planet/create_news_notification.html")
    elif request.method == 'POST':
        try:
            data_dic = request.form.to_dict()
            res = common_create_news_notification(data=data_dic)
            if res.get("code") == 0:
                return jsonify({"status": 'success', "msg": res.get('info')})
            return jsonify({"msg": res.get("info")})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")


# 编辑动态信息
@planet.route("/modify_news_notification", methods=['GET', 'POST'])
def modify_news_notification():
    if request.method == 'GET':
        try:
            sn =request.args.get("sn")
            res = common_modify_news_notification(sn=sn, flag=True)
            if res.get("code") == 0:
                return render_template("planet/modify_news_notification.html", data=res.get('info'))
            current_app.logger.error("modify_news_notification - GET ERROR!")
            return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            data_dic = request.form.to_dict()
            res = common_modify_news_notification(data=data_dic)
            if res.get("code") == 0:
                return jsonify({"status": 'success', "msg": res.get('info')})
            return jsonify({"msg": res.get("info")})
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
