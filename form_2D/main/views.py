from flask import Blueprint, url_for, redirect
from flask_login import login_required, current_user

main = Blueprint(
    "main",
     __name__,
     template_folder="templates",
     static_folder="static"
)

@main.route("/", methods=["GET"])
@login_required
def index():
    return redirect(url_for("seafile_client.index"))
