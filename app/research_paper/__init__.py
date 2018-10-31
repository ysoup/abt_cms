from flask import Blueprint
research_paper = Blueprint('research_paper', __name__)
from . import views
