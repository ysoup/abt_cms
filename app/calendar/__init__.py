from flask import Blueprint
cal = Blueprint('calendar', __name__)
from . import calendar_views