"""
routes/__init__.py — Blueprint registry.
Import all blueprints here so app.py can do `from routes import *`.
"""
from routes.alumnos import alumnos_bp
from routes.asignaturas import asignaturas_bp
from routes.auditoria import auditoria_bp
from routes.auth import auth_bp
from routes.home import home_bp
from routes.matriculas import matriculas_bp
from routes.profesores import profesores_bp
from routes.transacciones import transacciones_bp
from routes.vista import vista_bp

__all__ = [
    "alumnos_bp",
    "asignaturas_bp",
    "auditoria_bp",
    "auth_bp",
    "home_bp",
    "matriculas_bp",
    "profesores_bp",
    "transacciones_bp",
    "vista_bp",
]
