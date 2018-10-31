from flask import Blueprint
version = Blueprint("sys_version", __name__)

from . import version_views
