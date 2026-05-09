"""routes/consultas_avanzadas.py — Consultas avanzadas del tema 13."""
from flask import Blueprint, render_template
from models import OperacionesConsultasAvanzadas

consultas_bp = Blueprint("consultas_avanzadas", __name__, url_prefix="/consultas-avanzadas")
_ops = OperacionesConsultasAvanzadas()


@consultas_bp.route("/")
def index():
    error = None
    row_number_rows = []
    grouping_sets_rows = []
    rollup_rows = []
    filter_rows = []
    try:
        row_number_rows = _ops.row_number_top_cursos()
        grouping_sets_rows = _ops.grouping_sets_matriculas()
        rollup_rows = _ops.rollup_matriculas()
        filter_rows = _ops.filter_semestres()
    except Exception as exc:
        error = str(exc)
    return render_template(
        "consultas_avanzadas/index.html",
        row_number_rows=row_number_rows,
        grouping_sets_rows=grouping_sets_rows,
        rollup_rows=rollup_rows,
        filter_rows=filter_rows,
        error=error,
    )
