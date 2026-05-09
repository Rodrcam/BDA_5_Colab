import argparse
from app import create_app
from config import SERVER_IP, SERVER_PORT
from database_menu import database_menu
from models import PostgreSQL, OperacionesAlumno, OperacionesProfesor, OperacionesCurso, OperacionesMatricula



def main():
    parser = argparse.ArgumentParser()

    # Añadir argumentos a la ejecucción del servidor
    parser.add_argument(
        "--db", "--database",
        action="store_true",
        help="Muestra el menu de configuración de la base de datos"
    )
    parser.add_argument(
        "--rs", "--runserver",
        action="store_true",
        help="Ejecuta el servidor de la base de datos"
    )

    # Generamos las instancias de los gestores de la base de datos
    postgres = PostgreSQL()
    gestor_alumno = OperacionesAlumno()
    gestor_profesor = OperacionesProfesor()
    gestor_curso = OperacionesCurso()
    gestor_matricula = OperacionesMatricula()

    # Manejo de argumentos
    args = parser.parse_args()

    if args.db:
        database_menu(
            pg=postgres,
            gestor_alumno=gestor_alumno,
            gestor_profesor=gestor_profesor,
            gestor_curso=gestor_curso,
            gestor_matricula=gestor_matricula,
        )
    elif args.rs:
        app = create_app()
        app.run(
            host = SERVER_IP,               
            port = SERVER_PORT,           
            debug= True
        )
    else: 
        parser.print_help()

if __name__ == "__main__":
    main()
    