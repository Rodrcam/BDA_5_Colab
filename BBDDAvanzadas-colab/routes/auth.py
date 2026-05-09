"""routes/auth.py — Login / logout using SQLite auth."""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import SQLiteAuth

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
_auth = SQLiteAuth()


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = _auth.verify_user(username, password)
        if user:
            session["user"] = user
            flash("Sesión iniciada correctamente.", "success")
            return redirect(url_for("home.home"))
        flash("Credenciales incorrectas.", "danger")
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
