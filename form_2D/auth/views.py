from flask import Blueprint, Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import bcrypt
from .forms import SignupForm, LoginForm, ProfileForm
from .models import db, Users
from form_2D import login_manager

auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static"
)

@auth.route('/signup', methods = ['POST', 'GET'])
def signup():
    form = SignupForm()
    
    # return str(request.form)
    if form.validate_on_submit():
        exist_user = Users.query.filter_by(email = form.email.data).first() 
        if exist_user is None:
            usr = Users(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                phone_nb=form.phone_nb.data,
                address=form.address.data
            )
            db.session.add(usr)
            db.session.commit()
            #login as user which were registered
            login_user(usr)
            
            return redirect(url_for("auth.login"))
        flash("User's email has been taken!")
    return render_template("auth/signup.html", title="Sign Up page", form = form)

@auth.route("/login", methods = ["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            usr = Users.query.filter_by(email = form.email.data).first()

            if usr and usr.check_password(form.password.data):
                login_user(usr)
                # next_page = request.arg.get('nexts')
                return redirect(url_for('main.index'))
            flash("Login is failed!")
        return render_template("auth/login.html", title = "Login page", form = form)

@auth.route("/profile", methods = ["POST","GET"])
@login_required
def profile():
    form = ProfileForm()
    existed_usr = Users.query.filter_by(id = current_user.id).first()
    if form.validate_on_submit():
        if existed_usr.check_password(form.old_password.data):
            existed_usr.username=form.username.data
            existed_usr.password = bcrypt.hashpw(form.new_password.data.encode('utf-8'), bcrypt.gensalt())
            existed_usr.email=form.email.data
            existed_usr.first_name=form.first_name.data
            existed_usr.last_name=form.last_name.data
            existed_usr.phone_nb=form.phone_nb.data
            existed_usr.address=form.address.data
            db.session.commit()
            return render_template("main/index.html", form = form, user = current_user)
        flash("Your old password is not correct!")
    return render_template("auth/profile.html", form = form, user = current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))

@login_manager.user_loader
def load_user(user_id):
    """Check if user is logged-in on every page load."""
    if user_id is not None:
        return Users.query.get(user_id)
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))
