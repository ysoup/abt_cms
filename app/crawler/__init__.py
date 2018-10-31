from flask import Blueprint
crawl = Blueprint('crawler', __name__)
from . import crawler_views