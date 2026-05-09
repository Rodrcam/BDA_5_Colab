"""
routes/asignaturas.py — Course listing, multilingual search, and creation.

Search modes:
  ilike       — case-insensitive ILIKE
  fulltext    — tsvector plainto_tsquery
  similarity  — pg_trgm similarity operator
  levenshtein — fuzzystrmatch Levenshtein distance
  i18n        — courses with a translation for a given lang key
  i18n_value  — ILIKE on translated course name
"""
import json
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import OperacionesCurso, OperacionesProfesor, Cursos

asignaturas_bp = Blueprint("asignaturas", __name__, url_prefix="/asignaturas")
_gestor = OperacionesCurso()
_gestor_prof = OperacionesProfesor()

_SEARCH_MODES = ("ilike", "fulltext", "similarity", "levenshtein", "i18n", "i18n_value")


def _run_search(mode: str, term: str, lang: str, max_dist: int) -> list:
    if mode == "ilike":
        return _gestor.search_ilike(term)
    if mode == "fulltext":
        return _gestor.search_fulltext(term)
    if mode == "similarity":
        return _gestor.search_similarity(term)
    if mode == "levenshtein":
        return _gestor.search_levenshtein(term, max_dist)
    if mode == "i18n":
        return _gestor.search_i18n(lang)
    if mode == "i18n_value":
        return _gestor.search_i18n_value(lang, term)
    return []


@asignaturas_bp.route("/")
def index():
    cursos = _gestor.get_all_courses()
    return render_template("asignaturas/index.html", cursos=cursos)


@asignaturas_bp.route("/buscar")
def buscar():
    term = request.args.get("q", "").strip()
    mode = request.args.get("mode", "ilike")
    lang = request.args.get("lang", "es")
    max_dist = int(request.args.get("max_dist", 3))

    resultados = []
    error = None
    if term or mode in ("i18n",):
        try:
            resultados = _run_search(mode, term, lang, max_dist)
        except Exception as exc:
            error = str(exc)

    return render_template(
        "asignaturas/index.html",
        cursos=resultados,
        search_term=term,
        search_mode=mode,
        search_lang=lang,
        search_max_dist=max_dist,
        search_modes=_SEARCH_MODES,
        error=error,
    )


@asignaturas_bp.route("/api/buscar")
def api_buscar():
    """JSON endpoint for search results."""
    term = request.args.get("q", "").strip()
    mode = request.args.get("mode", "ilike")
    lang = request.args.get("lang", "es")
    max_dist = int(request.args.get("max_dist", 3))
    try:
        rows = _run_search(mode, term, lang, max_dist)
        results = [
            {"id": str(r[0]), "nombre": r[1], "nombre_i18n": r[2] if len(r) > 2 else {}}
            for r in rows
        ]
        return jsonify({"ok": True, "results": results, "count": len(results)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@asignaturas_bp.route("/nueva", methods=["GET", "POST"])
def nueva():
    profesores = _gestor_prof.get_all_teachers()
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        nombre_es = request.form.get("nombre_es", "").strip()
        nombre_en = request.form.get("nombre_en", "").strip()
        nombre_ca = request.form.get("nombre_ca", "").strip()
        profesor_id = request.form.get("profesor_id", "").strip() or None

        if not nombre:
            flash("El nombre del curso es obligatorio.", "danger")
            return render_template("asignaturas/nueva.html", profesores=profesores)

        nombre_i18n = {}
        if nombre_es:
            nombre_i18n["es"] = nombre_es
        if nombre_en:
            nombre_i18n["en"] = nombre_en
        if nombre_ca:
            nombre_i18n["ca"] = nombre_ca
        # Fall back: use nombre as the Spanish name if not provided
        if not nombre_i18n.get("es"):
            nombre_i18n["es"] = nombre

        curso = Cursos(
            id=str(uuid.uuid4()),
            nombre=nombre,
            profesor_id=profesor_id,
            nombre_i18n=nombre_i18n,
        )
        try:
            _gestor.insert_one_course(curso=curso)
            flash("Asignatura añadida correctamente.", "success")
            return redirect(url_for("asignaturas.index"))
        except Exception as exc:
            flash(f"Error al insertar: {exc}", "danger")

    return render_template("asignaturas/nueva.html", profesores=profesores)
