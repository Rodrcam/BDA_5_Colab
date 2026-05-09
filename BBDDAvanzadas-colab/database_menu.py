import uuid
import random
import datetime
from faker import Faker
from models import PostgreSQL, OperacionesAlumno, OperacionesProfesor, OperacionesCurso, OperacionesMatricula
from models import Alumnos, Profesores, Cursos, Matriculas

_fake = Faker("es_ES")

_NOMBRES_CURSOS = [
    "Matemáticas I", "Matemáticas II", "Álgebra Lineal",
    "Cálculo Diferencial", "Cálculo Integral", "Estadística",
    "Programación I", "Programación II", "Bases de Datos",
    "Redes de Computadores", "Sistemas Operativos", "Inteligencia Artificial",
    "Física I", "Física II", "Química General",
    "Historia Universal", "Filosofía", "Inglés Técnico",
]


def clear_screen() -> None:
    import subprocess
    import platform
    if platform.system() == "Windows":
        subprocess.call('cls', shell=True)
    else:
        subprocess.call('clear', shell=True)


# --- Generadores sintéticos ---

def _gen_alumnos(n: int) -> list[Alumnos]:
    alumnos = []
    emails_usados: set[str] = set()
    for _ in range(n):
        nombre = _fake.name()
        base_email = _fake.email()
        email = base_email
        contador = 1
        while email in emails_usados:
            partes = base_email.split("@")
            email = f"{partes[0]}{contador}@{partes[1]}"
            contador += 1
        emails_usados.add(email)
        alumnos.append(Alumnos(id=str(uuid.uuid4()), nombre=nombre, email=email))
    return alumnos


def _gen_profesores(n: int) -> list[Profesores]:
    return [Profesores(id=str(uuid.uuid4()), nombre=_fake.name()) for _ in range(n)]


def _gen_cursos(profesores: list[Profesores], n: int) -> list[Cursos]:
    nombres = random.sample(_NOMBRES_CURSOS, min(n, len(_NOMBRES_CURSOS)))
    if n > len(nombres):
        extras = [f"Taller {_fake.word().capitalize()}" for _ in range(n - len(nombres))]
        nombres.extend(extras)
    return [
        Cursos(id=str(uuid.uuid4()), nombre=nombres[i], profesor_id=random.choice(profesores).id)
        for i in range(n)
    ]


def _gen_matriculas(
    alumnos: list[Alumnos],
    cursos: list[Cursos],
    max_por_alumno: int = 4,
) -> list[Matriculas]:
    matriculas: list[Matriculas] = []
    pares_usados: set[tuple] = set()
    for alumno in alumnos:
        cantidad = random.randint(1, min(max_por_alumno, len(cursos)))
        for curso in random.sample(cursos, cantidad):
            par = (alumno.id, curso.id)
            if par in pares_usados:
                continue
            pares_usados.add(par)
            created_at = _fake.date_time_between(
                start_date="-2y", end_date="now", tzinfo=datetime.timezone.utc
            )
            matriculas.append(Matriculas(alumno_id=alumno.id, curso_id=curso.id, created_at=created_at))
    return matriculas


def _seed_database(
    gestor_alumno: OperacionesAlumno,
    gestor_profesor: OperacionesProfesor,
    gestor_curso: OperacionesCurso,
    gestor_matricula: OperacionesMatricula,
    n_alumnos: int = 15,
    n_profesores: int = 5,
    n_cursos: int = 10,
    max_matriculas_por_alumno: int = 4,
) -> None:
    print(f"\nGenerando {n_profesores} profesores...")
    profesores = _gen_profesores(n_profesores)
    for p in profesores:
        gestor_profesor.insert_one_teacher(profesor=p)
    print(f"  {n_profesores} profesores insertados.")

    print(f"Generando {n_alumnos} alumnos...")
    alumnos = _gen_alumnos(n_alumnos)
    for a in alumnos:
        gestor_alumno.insert_one_student(alumno=a)
    print(f"  {n_alumnos} alumnos insertados.")

    print(f"Generando {n_cursos} cursos...")
    cursos = _gen_cursos(profesores, n_cursos)
    for c in cursos:
        gestor_curso.insert_one_course(curso=c)
    print(f"  {n_cursos} cursos insertados.")

    print(f"Generando matrículas (máx {max_matriculas_por_alumno} por alumno)...")
    matriculas = _gen_matriculas(alumnos, cursos, max_matriculas_por_alumno)
    for m in matriculas:
        gestor_matricula.insert_one_enrollment(matricula=m)
    print(f"  {len(matriculas)} matrículas insertadas.")

    print("\nSeed completado exitosamente.")


# --- Menú principal ---

def database_menu(
        pg: PostgreSQL,
        gestor_alumno: OperacionesAlumno,
        gestor_profesor: OperacionesProfesor,
        gestor_curso: OperacionesCurso,
        gestor_matricula: OperacionesMatricula,
    ):
    while True:
        clear_screen()
        print("Bienvenido al menú de la base de datos")
        print("Seleccione una opción (1-5)")
        print("1. Obtener información de la base de datos")
        print("2. Añadir contenido a la base de datos")
        print("3. Consultar información")
        print("4. Generar datos sintéticos (Faker)")
        print("5. Salir")

        try:
            user_input = int(input("> "))
        except ValueError:
            print("Opción no válida. Por favor, ingrese un número.")
            input("Presione Enter para continuar...")
            continue

        match user_input:
            case 1:
                get_version = pg.obtain_database_version()
                if get_version:
                    print("Información de la base de datos:")
                    print("Postgres:", get_version)
                input("Presione Enter para continuar...")

            case 2:
                while True:
                    clear_screen()
                    print("Ventana para la creación de contenido, seleccione una opción:")
                    print("1. Crear tablas")
                    print("2. Crear contenido manualmente")
                    print("3. Volver al menú principal")

                    try:
                        content_option = int(input("> "))
                    except ValueError:
                        print("Opción no válida. Por favor, ingrese un número.")
                        input("Presione Enter para continuar...")
                        continue

                    match content_option:
                        case 1:
                            pg.create_tables()
                            print("Tablas creadas exitosamente.")
                            input("Presione Enter para continuar...")
                        case 2:
                            print("Seleccione una operación a realizar:")
                            print("1. Ingresar alumno")
                            print("2. Ingresar profesor")
                            print("3. Ingresar curso")

                            try:
                                user_insert_input = int(input("> "))
                            except ValueError:
                                print("Opción no válida. Por favor, ingrese un número.")
                                input("Presione Enter para continuar...")
                                continue

                            match user_insert_input:
                                case 1:
                                    nombre = input("Ingrese el nombre del alumno.\n> ")
                                    email = input("Ingrese el correo del alumno.\n> ")
                                    alumno = Alumnos(id=str(uuid.uuid4()), nombre=nombre, email=email)
                                    gestor_alumno.insert_one_student(alumno=alumno)
                                    input("Presione Enter para continuar...")
                                case 2:
                                    nombre = input("Ingrese el nombre del profesor.\n> ")
                                    profesor = Profesores(id=str(uuid.uuid4()), nombre=nombre)
                                    gestor_profesor.insert_one_teacher(profesor=profesor)
                                    input("Presione Enter para continuar...")
                                case 3:
                                    nombre = input("Ingrese el nombre del curso.\n> ")
                                    profesor_id = input("Ingrese el ID del profesor.\n> ")
                                    curso = Cursos(id=str(uuid.uuid4()), nombre=nombre, profesor_id=profesor_id)
                                    gestor_curso.insert_one_course(curso=curso)
                                    input("Presione Enter para continuar...")
                        case 3:
                            break
                        case _:
                            print("Opción no disponible.")
                            input("Presione Enter para continuar...")

            case 3:
                print("Seleccione qué categoría desea consultar:")
                print("1. Alumnos")
                print("2. Profesores")
                print("3. Cursos")
                print("4. Matrículas")

                try:
                    user_select_input = int(input("> "))
                except ValueError:
                    print("Opción no válida. Por favor, ingrese un número.")
                    input("Presione Enter para continuar...")
                    continue

                match user_select_input:
                    case 1:
                        alumnos = gestor_alumno.get_all_students()
                        for alumno in alumnos:
                            print(alumno)
                        input("Presione Enter para continuar")
                    case 2:
                        profesores = gestor_profesor.get_all_teachers()
                        for profesor in profesores:
                            print(profesor)
                        input("Presione Enter para continuar")
                    case 3:
                        cursos = gestor_curso.get_all_courses()
                        for curso in cursos:
                            print(f"ID: {curso[0]} | Nombre: {curso[1]} | Profesor: {curso[2]}")
                        input("Presione Enter para continuar")
                    case 4:
                        matriculas = gestor_matricula.get_all_enrollments()
                        for m in matriculas:
                            print(f"Alumno: {m[0]} | Curso: {m[1]} | Fecha: {m[2]}")
                        input("Presione Enter para continuar")
                    case _:
                        print("Opción no implementada")
                        input("Presione Enter para continuar")

            case 4:
                clear_screen()
                print("=== Generación de datos sintéticos ===")
                print("Se crearán registros de prueba con Faker (es_ES).")
                print()
                try:
                    n_alumnos    = int(input("Número de alumnos        [15]: ").strip() or "15")
                    n_profesores = int(input("Número de profesores      [5]: ").strip() or "5")
                    n_cursos     = int(input("Número de cursos         [10]: ").strip() or "10")
                    max_mat      = int(input("Máx. materias por alumno  [4]: ").strip() or "4")
                except ValueError:
                    print("Valor inválido, se usarán los valores por defecto.")
                    n_alumnos, n_profesores, n_cursos, max_mat = 15, 5, 10, 4

                _seed_database(
                    gestor_alumno=gestor_alumno,
                    gestor_profesor=gestor_profesor,
                    gestor_curso=gestor_curso,
                    gestor_matricula=gestor_matricula,
                    n_alumnos=n_alumnos,
                    n_profesores=n_profesores,
                    n_cursos=n_cursos,
                    max_matriculas_por_alumno=max_mat,
                )
                input("Presione Enter para continuar...")

            case 5:
                break
            case _:
                print("Opción no válida.")
                input("Presione Enter para continuar...")
