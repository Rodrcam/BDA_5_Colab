"""routes/home.py — Landing page."""
from flask import Blueprint, render_template
from models import PostgreSQL

home_bp = Blueprint("home", __name__, url_prefix="/home")
_pg = PostgreSQL()


@home_bp.route("/")
def home():
    try:
        counts = _pg.get_counts()
        version = _pg.obtain_database_version()
    except Exception:
        counts = {}
        version = "No disponible"
    return render_template("home/home.html", counts=counts, version=version)
