"""routes/vista.py — Combined summary view: all entities in one page."""
from flask import Blueprint, render_template
from models import (
    OperacionesAlumno,
    OperacionesProfesor,
    OperacionesCurso,
    OperacionesMatricula,
)

vista_bp = Blueprint("vista", __name__, url_prefix="/vista")
_g_alumno = OperacionesAlumno()
_g_prof = OperacionesProfesor()
_g_curso = OperacionesCurso()
_g_mat = OperacionesMatricula()


@vista_bp.route("/")
def index():
    try:
        alumnos = _g_alumno.get_all_students()
        profesores = _g_prof.get_all_teachers()
        cursos = _g_curso.get_all_courses()
        matriculas = _g_mat.get_all_enrollments()
    except Exception as exc:
        alumnos = profesores = cursos = matriculas = []
    return render_template(
        "vista/index.html",
        alumnos=alumnos,
        profesores=profesores,
        cursos=cursos,
        matriculas=matriculas,
    )
