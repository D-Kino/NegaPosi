from flask import Blueprint, render_template
from common.models.game import Game

index_page = Blueprint("index_page", __name__)


@index_page.route("/")
def index():
    name = "hello"
    context = {"name": name}

    result = Game.query.all()
    context['result'] = result

    return render_template("index.html", **context)
