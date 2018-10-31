from flask import Blueprint
# 实例化 Blueprint 类，两个参数分别为蓝图的名字和蓝图所在的包或者模块，第二个通常填__name__即可。
customer = Blueprint("customers", __name__)

from . import customer_views, reservation_views


