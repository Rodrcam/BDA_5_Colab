"""routes/matriculas.py — Enrollment listing and JSONB extras search."""
import uuid
import json
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import OperacionesMatricula, OperacionesAlumno, OperacionesCurso, Matriculas

matriculas_bp = Blueprint("matriculas", __name__, url_prefix="/matriculas")
_gestor = OperacionesMatricula()
_gestor_alumno = OperacionesAlumno()
_gestor_curso = OperacionesCurso()


@matriculas_bp.route("/")
def index():
    matriculas = _gestor.get_all_enrollments()
    return render_template("matriculas/index.html", matriculas=matriculas)


@matriculas_bp.route("/buscar")
def buscar():
    json_filter = request.args.get("extras", "{}").strip()
    resultados = []
    error = None
    try:
        json.loads(json_filter)  # validate JSON before sending to DB
        resultados = _gestor.search_by_extras(json_filter)
    except json.JSONDecodeError:
        error = "Filtro JSON no válido."
    except Exception as exc:
        error = str(exc)
    return render_template(
        "matriculas/index.html",
        matriculas=resultados,
        json_filter=json_filter,
        error=error,
    )


@matriculas_bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    alumnos = _gestor_alumno.get_all_students()
    cursos = _gestor_curso.get_all_courses()
    if request.method == "POST":
        alumno_id = request.form.get("alumno_id", "").strip()
        curso_id = request.form.get("curso_id", "").strip()
        if not alumno_id or not curso_id:
            flash("Alumno y curso son obligatorios.", "danger")
            return render_template("matriculas/nueva.html", alumnos=alumnos, cursos=cursos)
        matricula = Matriculas(
            alumno_id=alumno_id,
            curso_id=curso_id,
            created_at=datetime.now(timezone.utc),
        )
        try:
            _gestor.insert_one_enrollment(matricula=matricula)
            flash("Matrícula registrada correctamente.", "success")
            return redirect(url_for("matriculas.index"))
        except Exception as exc:
            flash(f"Error al insertar: {exc}", "danger")
    return render_template("matriculas/nueva.html", alumnos=alumnos, cursos=cursos)
