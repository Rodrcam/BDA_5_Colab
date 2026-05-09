import uuid
import random
import datetime
from faker import Faker
from models import (
    OperacionesAlumno, OperacionesProfesor,
    OperacionesCurso, OperacionesMatricula,
    Alumnos, Profesores, Cursos, Matriculas,
)

fake = Faker("es_ES")

# Multilingual translations for seed data stored in nombre_i18n JSONB column
_I18N_MAP: dict[str, dict[str, str]] = {
    "Matemáticas I":           {"es": "Matemáticas I",           "en": "Mathematics I",           "ca": "Matemàtiques I"},
    "Matemáticas II":          {"es": "Matemáticas II",          "en": "Mathematics II",          "ca": "Matemàtiques II"},
    "Álgebra Lineal":          {"es": "Álgebra Lineal",          "en": "Linear Algebra",          "ca": "Àlgebra Lineal"},
    "Cálculo Diferencial":     {"es": "Cálculo Diferencial",     "en": "Differential Calculus",   "ca": "Càlcul Diferencial"},
    "Cálculo Integral":        {"es": "Cálculo Integral",        "en": "Integral Calculus",       "ca": "Càlcul Integral"},
    "Estadística":             {"es": "Estadística",             "en": "Statistics",              "ca": "Estadística"},
    "Programación I":          {"es": "Programación I",          "en": "Programming I",           "ca": "Programació I"},
    "Programación II":         {"es": "Programación II",         "en": "Programming II",          "ca": "Programació II"},
    "Bases de Datos":          {"es": "Bases de Datos",          "en": "Databases",               "ca": "Bases de Dades"},
    "Redes de Computadores":   {"es": "Redes de Computadores",   "en": "Computer Networks",       "ca": "Xarxes de Computadors"},
    "Sistemas Operativos":     {"es": "Sistemas Operativos",     "en": "Operating Systems",       "ca": "Sistemes Operatius"},
    "Inteligencia Artificial": {"es": "Inteligencia Artificial", "en": "Artificial Intelligence", "ca": "Intel·ligència Artificial"},
    "Física I":                {"es": "Física I",                "en": "Physics I",               "ca": "Física I"},
    "Física II":               {"es": "Física II",               "en": "Physics II",              "ca": "Física II"},
    "Química General":         {"es": "Química General",         "en": "General Chemistry",       "ca": "Química General"},
    "Historia Universal":      {"es": "Historia Universal",      "en": "World History",           "ca": "Història Universal"},
    "Filosofía":               {"es": "Filosofía",               "en": "Philosophy",              "ca": "Filosofia"},
    "Inglés Técnico":          {"es": "Inglés Técnico",          "en": "Technical English",       "ca": "Anglès Tècnic"},
}

NOMBRES_CURSOS = list(_I18N_MAP.keys())


def _gen_alumnos(n: int) -> list[Alumnos]:
    alumnos = []
    emails_usados: set[str] = set()
    for _ in range(n):
        nombre = fake.name()
        base_email = fake.email()
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
    return [
        Profesores(id=str(uuid.uuid4()), nombre=fake.name())
        for _ in range(n)
    ]


def _gen_cursos(profesores: list[Profesores], n: int) -> list[Cursos]:
    nombres = random.sample(NOMBRES_CURSOS, min(n, len(NOMBRES_CURSOS)))
    if n > len(nombres):
        extras = [f"Taller {fake.word().capitalize()}" for _ in range(n - len(nombres))]
        nombres.extend(extras)
    cursos = []
    for i in range(n):
        nombre = nombres[i]
        nombre_i18n = _I18N_MAP.get(nombre, {"es": nombre})
        cursos.append(Cursos(
            id=str(uuid.uuid4()),
            nombre=nombre,
            profesor_id=random.choice(profesores).id,
            nombre_i18n=nombre_i18n,
        ))
    return cursos


def _gen_matriculas(
    alumnos: list[Alumnos],
    cursos: list[Cursos],
    max_por_alumno: int = 4,
) -> list[Matriculas]:
    matriculas: list[Matriculas] = []
    pares_usados: set[tuple] = set()
    for alumno in alumnos:
        cantidad = random.randint(1, min(max_por_alumno, len(cursos)))
        cursos_elegidos = random.sample(cursos, cantidad)
        for curso in cursos_elegidos:
            par = (alumno.id, curso.id)
            if par in pares_usados:
                continue
            pares_usados.add(par)
            created_at = fake.date_time_between(
                start_date="-2y", end_date="now",
                tzinfo=datetime.timezone.utc,
            )
            matriculas.append(
                Matriculas(alumno_id=alumno.id, curso_id=curso.id, created_at=created_at)
            )
    return matriculas


def seed_database(
    n_alumnos: int = 15,
    n_profesores: int = 5,
    n_cursos: int = 10,
    max_matriculas_por_alumno: int = 4,
) -> None:
    gestor_alumno = OperacionesAlumno()
    gestor_profesor = OperacionesProfesor()
    gestor_curso = OperacionesCurso()
    gestor_matricula = OperacionesMatricula()

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
