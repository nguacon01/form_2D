from flask import Flask, flash, Blueprint, render_template, redirect, url_for

errors = Blueprint(
    "errors", 
    __name__,
    template_folder="templates",
    static_folder="static"
)
#page not found
@errors.app_errorhandler(404)
def error_404(error):
    return render_template("errors/404.html"), 404

# permision denided
@errors.app_errorhandler(403)
def error_403(error):
    return render_template("errors/403.html"), 403

# server not found
@errors.app_errorhandler(500)
def error_500(error):
    return render_template("errors/500.html"), 500