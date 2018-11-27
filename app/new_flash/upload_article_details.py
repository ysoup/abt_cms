# encoding=utf-8
from flask_login import login_required
from flask import request, render_template, jsonify, make_response, flash, abort, url_for, redirect, session, Flask, g, \
    current_app
from . import new_flash
from app.models import AccountManage, ArticleManage, ArticleUploadManage, InformationPlatform, NewInformationCategory, \
    ArticleUploadDetails


# 山川详情列表
@new_flash.route('/upload_details_list', methods=['GET'])
@login_required
def upload_details_list():
    try:
        upload_id = request.args.get('upload_id')
        rows = ArticleUploadDetails.query.filter_by(upload_id=upload_id)
        success_ls = []
        failed_ls = []
        for x in rows:
            dic = {}
            dic["id"] = x.id
            dic["article_title"] = x.article_title
            dic["account_name"] = x.account_name
            dic["article_type"] = x.article_type
            dic["article_category"] = x.article_category
            dic["send_status"] = x.send_status
            dic["create_time"] = x.create_time
            dic["desc"] = x.desc
            if x.send_status == 1:
                success_ls.append(dic)
            else:
                failed_ls.append(dic)

        # 账户分类
        platform_category = NewInformationCategory.query
        category_ls = []
        if platform_category:
            for x in platform_category:
                dic = {}
                dic["id"] = x.id
                dic["category_name"] = x.category_name
                category_ls.append(dic)

        return render_template("article/upload_article_details.html", success_ls=success_ls, failed_ls=failed_ls,
                               category_ls=category_ls)
        # upload_id = request.args.get('upload_id')
        # page = request.args.get('page', 1, type=int)
        # pagination = ArticleUploadDetails.query.order_by(AccountManage.create_time.desc()).paginate(page, per_page=10,
        #                                                                                      error_out=False)
        # data = pagination.items
        # # 账户类型
        # types_ls = [
        #     {0: "3级图文原创"},
        #     {1: "2级图文原创"},
        #     {2: "3级非图文原创"},
        #     {3: "2级非图文原创"}
        # ]
        # # 账户平台
        # platform_rows = InformationPlatform.query
        # platform_ls = []
        # if platform_rows:
        #     for x in platform_rows:
        #         dic = {}
        #         dic["id"] = x.id
        #         dic["platform_name"] = x.platform_name
        #         platform_ls.append(dic)
        #
        # # 账户分类
        # platform_category = NewInformationCategory.query
        # category_ls = []
        # if platform_category:
        #     for x in platform_category:
        #         dic = {}
        #         dic["id"] = x.id
        #         dic["category_name"] = x.category_name
        #         category_ls.append(dic)
        #
        # return render_template('account/account_manage_list.html', data=data,
        #                        types_ls=types_ls,
        #                        platform_ls=platform_ls,
        #                        category_ls=category_ls,
        #                        pagination=pagination)

    except Exception as e:
        current_app.logger.error(e)
        return render_template("404.html")
