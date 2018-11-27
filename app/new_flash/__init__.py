from flask import Blueprint
new_flash = Blueprint('new_flash', __name__)
from . import new_flash_list, upload_article_details
