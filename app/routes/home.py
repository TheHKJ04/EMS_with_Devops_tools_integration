from flask import Blueprint, render_template, redirect, url_for, session, request

home_bp=Blueprint("home",__name__)

@home_bp.route("/")
def root():
    return redirect(url_for("auth.login"))

@home_bp.route("/home")
def home():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return render_template("home.html", name="Python Programming")
