"""routes/auditoria.py — DB version and record counts."""
from flask import Blueprint, render_template
from models import PostgreSQL

auditoria_bp = Blueprint("auditoria", __name__, url_prefix="/auditoria")
_pg = PostgreSQL()


@auditoria_bp.route("/")
def index():
    try:
        version = _pg.obtain_database_version()
        counts = _pg.get_counts()
    except Exception as exc:
        version = "Error"
        counts = {}
    return render_template("auditoria/index.html", version=version, counts=counts)
