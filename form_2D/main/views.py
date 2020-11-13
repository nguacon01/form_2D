from flask import Blueprint, url_for, redirect

main = Blueprint(
    "main",
     __name__,
     template_folder="templates",
     static_folder="static"
)

@main.route("/", methods=["GET"])
def index():
    return redirect(url_for("seafile_client.index"))
