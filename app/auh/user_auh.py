from flask import render_template, redirect, request, session, g, jsonify, current_app
from flask_login import login_required, current_user
from cms_server import db
from app import models
from app.main.form import LoginForm
# 导入蓝本 main
from . import user_b


@user_b.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@user_b.route('/user_list', methods=['GET', 'POST'])
@login_required
def user_list():
    page = request.args.get('page', 1, type=int)
    pagination = models.User.query.order_by(models.User.last_seen.desc()).paginate(page,per_page=5,error_out=False)
    data = pagination.items
    return render_template('user/user_list.html', data=data, pagination=pagination)


@user_b.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'GET':
        return render_template('user/add_user.html')
    elif request.method == 'POST':
        try:
            new_user = models.User(email=request.form['username'], password=request.form['password'])
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'success': 'ok'})
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
    else:
        return render_template('404.html')



@user_b.route('/del_user', methods=['GET', 'POST'])
@login_required
def del_user():
    if request.method == "POST":
        if current_user.id in [1,2,3]:
            try:
                user_obj = models.User.query.filter_by(id=request.form['id']).first()
                db.session.delete(user_obj)
                db.session.commit()
                return jsonify({'success': 'ok'})
            except  Exception as e:
                current_app.logger.error(e)
                db.session.rollback()
        else:
            return render_template('404.html')