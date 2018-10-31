# from os.path import dirname, join
from flask import render_template, request, current_app, jsonify
from flask_login import login_required
from . import research_paper
from .generate_paper import generate_paper


@research_paper.route('/research-paper/templates', methods=['GET'])
@login_required
def templates():
    try:
        pagination = ''
        data = ''
        return render_template("research_paper/templates.html", data=data, pagination=pagination)
    except Exception as e:
        current_app.logger.error(e)


@research_paper.route('/research-paper/generate_paper', methods=['GET'])
@login_required
def generate_paper_view():
    try:
        # here = dirname(__file__)
        # tpl_doc = join(here, 'templates/paper_tpl.docx')
        tpl_doc = 'app/static/research_paper/templates/paper_tpl.docx'
        output_paper = generate_paper(tpl_doc)
        if output_paper != '':
            output_paper = '/static/' + output_paper.split("/static/")[1]
        current_app.logger.info("generate_paper %s" % output_paper)
        if output_paper:
            return jsonify({"status": "ok", "output_paper": output_paper})
        else:
            return jsonify({"status": "failed", "error_msg": 'fail to generate paper.'})
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"status": "failed", "error_msg": 'fail to generate paper: %s' % e})

