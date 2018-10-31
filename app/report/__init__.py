from flask import Blueprint
rep = Blueprint('report', __name__)
from . import report_list