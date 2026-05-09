"""routes/profesores.py — Teacher listing."""
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import OperacionesProfesor, Profesores

profesores_bp = Blueprint("profesores", __name__, url_prefix="/profesores")
_gestor = OperacionesProfesor()


@profesores_bp.route("/")
def index():
    profesores = _gestor.get_all_teachers()
    return render_template("profesores/index.html", profesores=profesores)


@profesores_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es obligatorio.", "danger")
            return render_template("profesores/nuevo.html")
        profesor = Profesores(id=str(uuid.uuid4()), nombre=nombre)
        try:
            _gestor.insert_one_teacher(profesor=profesor)
            flash("Profesor añadido correctamente.", "success")
            return redirect(url_for("profesores.index"))
        except Exception as exc:
            flash(f"Error al insertar: {exc}", "danger")
    return render_template("profesores/nuevo.html")
