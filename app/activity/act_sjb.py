import json
from flask import request, render_template, jsonify, current_app
from flask_login import login_required
from common.act.act_lx import common_user, common_delete_user, common_act_info, common_add_act
# 导入蓝图
from . import act
from ..utils.Pagination import Pagination

PROJECTNO = str(5)

WorldCode = {
            "CN":"中国", "HK":"香港", "MO":"澳门", "TW":"台湾", "AE":"阿联酋", "AF":"阿富汗",
            "AL":"阿尔巴尼亚", "AZ":"阿塞拜疆", "BD":"孟加拉", "BH":"巴林", "BN":"文莱", "BT":"不丹",
            "ID":"印度尼西亚", "CY":"塞浦路斯", "IL":"以色列", "IN":"印度", "IQ":"伊拉克", "IR":"伊朗",
            "JO":"约旦", "JP":"日本", "KH":"柬埔寨", "KP":"韩国", "KR":"北朝鲜", "KW":"科威特",
            "KZ":"哈萨克斯坦", "LA":"老挝", "LB":"黎巴嫩", "LU":"卢森堡", "MN":"蒙古", "UZ":"乌兹别克斯坦",
            "MV":"马尔代夫", "MY":"马来西亚", "PH":"菲律宾", "PK":"巴基斯坦", "NP":"尼泊尔", "SA":"沙特阿拉伯",
            "OM":"阿曼", "QA":"卡塔尔", "VN":"越南", "YE":"也门", "SG":"新加坡", "SY":"叙利亚",
            "TH":"泰国", "TJ":"哈吉克斯坦", "TM":"土库曼斯坦", "EC":"厄瓜多尔", "CL":"智利", "AR":"阿根廷",
            "BO":"玻利维亚", "BR":"巴西", "CO":"哥伦比亚", "GY":"圭亚那", "PY":"巴拉圭", "PE":"秘鲁",
            "UY":"乌拉圭", "HN":"洪都拉斯", "HT":"海地", "GT":"危地马拉", "GD":"格林纳达", "BM":"百慕大",
            "BS":"巴哈马", "CA":"加拿大", "CR":"哥斯达黎加", "CU":"古巴", "MX":"墨西哥", "JM":"牙买加",
            "US":"美国", "VE":"委内瑞拉", "PA":"巴拿马", "NI":"尼加拉瓜", "HU":"匈牙利", "HRV":"克罗地亚",
            "IE":"爱尔兰", "LT":"立陶宛", "AT":"奥地利", "BE":"比利时", "BG":"保加利亚", "CH":"瑞士",
            "CZ":"捷克共和国", "DE":"德国", "DK":"丹麦", "EE":"爱沙尼亚", "ES":"西班牙", "FI":"芬兰",
            "FR":"法国", "GB":"英国", "GR":"希腊", "IS":"冰岛", "IT":"意大利", "LV":"拉脱维亚",
            "MC":"摩纳哥", "MD":"摩尔多瓦", "MT":"马耳他", "NL":"荷兰", "NO":"挪威", "PL":"波兰",
            "PT":"葡萄牙", "RO":"罗马尼亚", "RU":"俄罗斯", "VA":"梵蒂冈", "YU":"南斯拉夫", "SE":"瑞典",
            "SK":"斯洛伐克", "SM":"圣马力诺", "UA":"乌克兰", "UK":"英国", "AU":"澳大利亚", "CK":"库克群岛",
            "FJ":"斐济", "GU":"关岛", "NZ":"新西兰", "PG":"巴布亚新几内亚", "TO":"汤加", "ET":"埃塞俄比亚",
            "KE":"肯尼亚", "LY":"利比亚", "MA":"摩洛哥", "MG":"马达加斯加", "ML":"马里", "MR":"毛里塔尼亚",
            "MU":"毛里求斯", "MZ":"莫桑比克", "NA":"纳米比亚", "NE":"尼日尔", "NG":"尼日利亚", "TZ":"坦桑尼亚",
            "TN":"突尼斯", "SN":"塞内加尔", "SO":"索马里", "RW":"卢旺达", "SD":"苏丹", "UG":"乌干达",
            "EG":"埃及", "DZ":"阿尔及利亚", "CV":"佛得角", "AO":"安哥拉", "BI":"布隆迪", "BJ":"贝宁",
            "CF":"中非", "CG":"刚果", "BW":"博茨瓦纳", "CM":"喀麦隆", "GH":"加纳", "GM":"冈比亚",
            "GN":"几内亚", "GQ":"赤道几内亚", "GA":"加蓬", "ZA":"南非", "ZM":"赞比亚", "ZR":"扎伊尔",
            "ZW":"津巴布韦"
            }


# 世界杯活动主页面
@act.route("/act_sjb")
@login_required
def act_sjb():
    try:
        if request.args.get("stage"):
            res = json.loads(common_user("stage", request.args.get("stage"), PROJECTNO))
        elif request.args.get("telephone"):
            res = json.loads(common_user("telephone", request.args.get("telephone"), PROJECTNO))
        else:
            res = json.loads(common_user("","", PROJECTNO))
        res1 = json.loads(common_act_info(PROJECTNO))
        if res['code'] == 0:
            l = res.get("info")
            l_act = res1.get("data")[0].get("stageinfo")
            pager_obj = Pagination(request.args.get("page", 1), len(l), request.path, request.args, per_page_count=50)
            # pager_obj_act = Pagination(request.args.get("page", 1), len(l_act), request.path, request.args, per_page_count=100)
            data = l[pager_obj.start:pager_obj.end]
            for data1 in data:
                world_list = []
                result = data1.get("remark").split(",")
                for re in result:
                    for world_code in WorldCode:
                        if re == world_code:
                            re = WorldCode[world_code]
                            world_list.append(re)
                data1["remark"] = world_list
            # data_act = l_act[pager_obj_act.start:pager_obj_act.end]
            html = pager_obj.page_html()
            # html_act = pager_obj_act.page_html()
            return render_template("activity/sjb/act_sjb.html", data=data, html=html, data_act=l_act)
        else:
            current_app.logger.error("act_sjb.py- res.code!= 0", res.get('code'))
            return render_template("404.html")
    except Exception as e :
        current_app.logger.error(e)
        return render_template("404.html")

# 删除用户
@act.route("/delete_user_sjb", methods=['GET', 'POST'])
@login_required
def delete_user_sjb():
    if request.method == "POST":
        try:
            id = request.form['id']
            stage = request.form["stage"]
            data = common_delete_user(id, stage, PROJECTNO)
            if data.status_code == 201:
                if json.loads(data.text).get('code') == 0:
                    return jsonify({'success': 'ok'})
            return jsonify({'failed': '未删除成功'})
        except Exception as e:
            current_app.logger.error(e)
        return jsonify({'failed': '删除失败，请重试'})

# 新增当前活动轮数
@act.route("/add_act_sjb", methods=["GET", "POST"])
@login_required
def add_act_sjb():
    if request.method == 'GET':
        return render_template("activity/sjb/add_act.html")
    elif request.method == 'POST':
        try:
            if json.loads(common_act_info(PROJECTNO))['code'] == 0:
                data = json.loads(common_act_info(PROJECTNO)).get("data")[0]
                data_info = data.get("stageinfo")
                end_time = request.form.get("end_time")
                per_amount = str(float(request.form.get("per_amount"))/1000)
                stage = len(data_info)+1
                start_time = request.form.get("start_time")
                total_amount = request.form.get("total_amount")
                total_member = request.form.get("total_member")
                info = {'asset_id': 'btc', 'end_time': end_time, 'member': 0, 'per_amount': per_amount, 'stage': str(stage), 'start_time': start_time, 'total_amount': total_amount, 'total_member': total_member}
                data_info.append(info)
                if not data.get("duration"):
                    data['duration'] = ""
                res = common_add_act(data)
                if json.loads(res).get('code') == 0:
                    return jsonify({'success': 'ok'})
            return jsonify({'failed': '添加失败'})
        except Exception as e :
            current_app.logger.error(e)
            return jsonify({'failed': '删除失败，请重试'})

# 编辑当前活动
@act.route("/modify_act_sjb", methods=["GET", "POST"])
@login_required
def modify_act():
    if request.method == 'GET':
        try:
            stage = request.args.get("stage")
            res = json.loads(common_act_info(PROJECTNO))
            if res['code'] == 0:
                l_act = res.get("data")[0].get("stageinfo")
                for item in l_act:
                    if stage == item["stage"]:
                        return render_template("activity/sjb/modify_act.html", data=item)
                current_app.logger.error("act_sjb.py- 97, stage is not found!")
                return render_template("404.html")
        except Exception as e:
            current_app.logger.error(e)
            return render_template("404.html")
    elif request.method == 'POST':
        try:
            if json.loads(common_act_info(PROJECTNO))['code'] == 0:
                data = json.loads(common_act_info(PROJECTNO)).get("data")[0]
                data_info = data.get("stageinfo")
                end_time = request.form.get("end_time")
                stage = request.form.get("stage")
                start_time = request.form.get("start_time")
                total_amount = request.form.get("total_amount")
                total_member = request.form.get("total_member")
                for item in data_info:
                    if stage == item["stage"]:
                        item["end_time"] = end_time
                        item["start_time"] = start_time
                        item["total_amount"] = total_amount
                        item["total_member"] = total_member
                if not data.get("duration"):
                    data['duration'] = ""
                res = common_add_act(data)
                if json.loads(res).get('code') == 0:
                    return jsonify({'success': 'ok'})
                return jsonify({'failed': '编辑失败'})
        except Exception as e :
            current_app.logger.error(e)
            return jsonify({'failed': '在POST请求时出现问题。'})