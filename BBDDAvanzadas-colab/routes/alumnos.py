"""routes/alumnos.py — Student listing and unaccent/jsonb search."""
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import OperacionesAlumno, Alumnos

alumnos_bp = Blueprint("alumnos", __name__, url_prefix="/alumnos")
_gestor = OperacionesAlumno()


@alumnos_bp.route("/")
def index():
    alumnos = _gestor.get_all_students()
    return render_template("alumnos/index.html", alumnos=alumnos)


@alumnos_bp.route("/buscar")
def buscar():
    term = request.args.get("q", "").strip()
    mode = request.args.get("mode", "unaccent")
    resultados = []
    if term:
        if mode == "jsonb_key":
            resultados = _gestor.search_by_jsonb_key(term)
        else:
            resultados = _gestor.search_by_name_unaccent(term)
    return render_template(
        "alumnos/index.html",
        alumnos=resultados,
        search_term=term,
        search_mode=mode,
    )


@alumnos_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        email = request.form.get("email", "").strip()
        if not nombre or not email:
            flash("Nombre y email son obligatorios.", "danger")
            return render_template("alumnos/nuevo.html")
        alumno = Alumnos(id=str(uuid.uuid4()), nombre=nombre, email=email)
        try:
            _gestor.insert_one_student(alumno=alumno)
            flash("Alumno añadido correctamente.", "success")
            return redirect(url_for("alumnos.index"))
        except Exception as exc:
            flash(f"Error al insertar: {exc}", "danger")
    return render_template("alumnos/nuevo.html")
