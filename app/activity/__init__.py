from flask import Blueprint
#实例化 Blueprint 类，两个参数分别为蓝本的名字和蓝本所在包或模块，第二个通常填 __name__ 即可
act = Blueprint('activity', __name__)
from . import act_lx, act_sjb, act_byj, activity_lx