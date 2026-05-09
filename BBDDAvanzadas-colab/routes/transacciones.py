"""
routes/transacciones.py — Demonstrates PostgreSQL transactions.

Provides a UI endpoint that shows how the @with_transaction decorator
works: both inserting a professor and a course in the same transaction,
rolling back if either fails.
"""
import json
import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import OperacionesProfesor, OperacionesCurso, Profesores, Cursos
from models.db.decorators import with_transaction
from models.db import querys as Q

transacciones_bp = Blueprint("transacciones", __name__, url_prefix="/transacciones")


@with_transaction
def _insert_profesor_y_curso(
    profesor: Profesores,
    curso: Cursos,
    *,
    conn,
    cursor,
) -> None:
    """Insert both a professor and a course atomically."""
    cursor.execute(Q.SQL_INSERT_PROFESOR, (profesor.id, profesor.nombre))
    nombre_i18n_json = json.dumps(curso.nombre_i18n, ensure_ascii=False)
    cursor.execute(
        Q.SQL_INSERT_CURSO,
        (curso.id, curso.nombre, nombre_i18n_json, curso.profesor_id),
    )


@transacciones_bp.route("/")
def index():
    return render_template("transacciones/index.html")


@transacciones_bp.route("/demo", methods=["POST"])
def demo():
    nombre_prof = request.form.get("nombre_profesor", "").strip()
    nombre_curso = request.form.get("nombre_curso", "").strip()
    forzar_error = request.form.get("forzar_error") == "1"

    if not nombre_prof or not nombre_curso:
        flash("Nombre de profesor y curso son obligatorios.", "danger")
        return redirect(url_for("transacciones.index"))

    profesor = Profesores(id=str(uuid.uuid4()), nombre=nombre_prof)
    # If forzar_error, intentionally use a bad profesor_id to trigger FK violation
    curso = Cursos(
        id=str(uuid.uuid4()),
        nombre=nombre_curso,
        profesor_id=profesor.id if not forzar_error else str(uuid.uuid4()),
        nombre_i18n={"es": nombre_curso},
    )

    try:
        _insert_profesor_y_curso(profesor, curso)
        flash(
            f"Transacción completada: profesor '{nombre_prof}' y curso '{nombre_curso}' insertados.",
            "success",
        )
    except Exception as exc:
        flash(f"Transacción revertida (rollback): {exc}", "danger")

    return redirect(url_for("transacciones.index"))
