"""
entities.py — Pure-Python dataclasses representing DB rows.
No SQL here — all queries live in models/db/querys.py.
"""
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Alumnos:
    id: str
    nombre: str
    email: str
    extras: dict = field(default_factory=dict)


@dataclass
class Profesores:
    id: str
    nombre: str


@dataclass
class Cursos:
    id: str
    nombre: str
    profesor_id: str
    nombre_i18n: dict = field(default_factory=dict)


@dataclass
class Matriculas:
    alumno_id: str
    curso_id: str
    created_at: datetime = field(default_factory=lambda: datetime.utcnow())
    extras: dict = field(default_factory=dict)
