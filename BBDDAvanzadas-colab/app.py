import os
from flask import Flask, redirect, url_for
from config import TEMPLATE_DIR
from routes import *

def create_app() -> Flask:
    app = Flask(__name__, template_folder=TEMPLATE_DIR)
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-bda-practica3')

    # Registro de blueprints
    app.register_blueprint(alumnos_bp,      name="alumnos")
    app.register_blueprint(asignaturas_bp,  name="asignaturas")
    app.register_blueprint(auditoria_bp,    name="auditoria")
    app.register_blueprint(auth_bp,         name="auth")
    app.register_blueprint(home_bp,         name="home")
    app.register_blueprint(matriculas_bp,   name="matriculas")
    app.register_blueprint(profesores_bp,   name="profesores")
    app.register_blueprint(transacciones_bp,name="transacciones")
    app.register_blueprint(vista_bp,        name="vista")

    # Redireccionamiento
    @app.route("/")
    def index():
        return redirect(url_for('home.home'))

    return app
