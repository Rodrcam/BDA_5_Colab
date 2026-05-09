"""
psql.py — PostgreSQL data-access classes.

All SQL strings are imported from models.db.querys — none are written here.
All database I/O uses the @with_cursor / @with_transaction decorators.
"""
import json
from models.db.decorators import with_cursor, with_transaction
from models.db import querys as Q
from models.entities.entities import Alumnos, Profesores, Cursos, Matriculas


# ---------------------------------------------------------------------------
# Schema management
# ---------------------------------------------------------------------------

class PostgreSQL:
    """Handles schema setup: extensions, tables, indexes, version info."""

    @with_transaction
    def setup_extensions(self, *, conn, cursor):
        for sql in Q.SQL_CREATE_EXTENSIONS:
            cursor.execute(sql)

    @with_cursor
    def create_tables(self, *, cursor):
        cursor.execute(Q.SQL_CREATE_TABLE_PROFESORES)
        cursor.execute(Q.SQL_CREATE_TABLE_ALUMNOS)
        cursor.execute(Q.SQL_CREATE_TABLE_CURSOS)
        cursor.execute(Q.SQL_CREATE_TABLE_MATRICULAS)
        for idx_sql in Q.SQL_CREATE_INDEXES:
            cursor.execute(idx_sql)

    @with_cursor
    def obtain_database_version(self, *, cursor) -> str | None:
        cursor.execute(Q.SQL_GET_VERSION)
        row = cursor.fetchone()
        return row[0] if row else None

    @with_cursor
    def get_counts(self, *, cursor) -> dict:
        cursor.execute(Q.SQL_GET_COUNTS)
        row = cursor.fetchone()
        if row is None:
            return {}
        return {
            "alumnos":    row[0],
            "profesores": row[1],
            "cursos":     row[2],
            "matriculas": row[3],
        }


# ---------------------------------------------------------------------------
# Alumnos
# ---------------------------------------------------------------------------

class OperacionesAlumno:

    @with_cursor
    def insert_one_student(self, alumno: Alumnos, *, cursor) -> None:
        cursor.execute(Q.SQL_INSERT_ALUMNO, (alumno.id, alumno.nombre, alumno.email))

    @with_cursor
    def get_all_students(self, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_GET_ALL_ALUMNOS)
        return cursor.fetchall()

    @with_cursor
    def search_by_name_unaccent(self, term: str, *, cursor) -> list[tuple]:
        """Case- and accent-insensitive search on nombre using unaccent()."""
        cursor.execute(Q.SQL_SEARCH_ALUMNOS_UNACCENT, (f"%{term}%",))
        return cursor.fetchall()

    @with_cursor
    def search_by_jsonb_key(self, key: str, *, cursor) -> list[tuple]:
        """Return alumnos whose extras JSONB contains the given key."""
        cursor.execute(Q.SQL_SEARCH_ALUMNOS_JSONB_KEY, (key,))
        return cursor.fetchall()


# ---------------------------------------------------------------------------
# Profesores
# ---------------------------------------------------------------------------

class OperacionesProfesor:

    @with_cursor
    def insert_one_teacher(self, profesor: Profesores, *, cursor) -> None:
        cursor.execute(Q.SQL_INSERT_PROFESOR, (profesor.id, profesor.nombre))

    @with_cursor
    def get_all_teachers(self, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_GET_ALL_PROFESORES)
        return cursor.fetchall()


# ---------------------------------------------------------------------------
# Cursos
# ---------------------------------------------------------------------------

class OperacionesCurso:

    @with_cursor
    def insert_one_course(self, curso: Cursos, *, cursor) -> None:
        nombre_i18n_json = json.dumps(curso.nombre_i18n, ensure_ascii=False)
        cursor.execute(
            Q.SQL_INSERT_CURSO,
            (curso.id, curso.nombre, nombre_i18n_json, curso.profesor_id),
        )

    @with_cursor
    def get_all_courses(self, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_GET_ALL_CURSOS)
        return cursor.fetchall()

    @with_cursor
    def search_ilike(self, term: str, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_SEARCH_CURSOS_ILIKE, (f"%{term}%",))
        return cursor.fetchall()

    @with_cursor
    def search_fulltext(self, term: str, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_SEARCH_CURSOS_FULLTEXT, (term,))
        return cursor.fetchall()

    @with_cursor
    def search_similarity(self, term: str, *, cursor) -> list[tuple]:
        """pg_trgm similarity search — requires pg_trgm extension."""
        cursor.execute(Q.SQL_SEARCH_CURSOS_SIMILARITY, (term, term))
        return cursor.fetchall()

    @with_cursor
    def search_levenshtein(self, term: str, max_dist: int = 3, *, cursor) -> list[tuple]:
        """fuzzystrmatch Levenshtein distance search."""
        cursor.execute(Q.SQL_SEARCH_CURSOS_LEVENSHTEIN, (term, term, max_dist))
        return cursor.fetchall()

    @with_cursor
    def search_i18n(self, lang: str, *, cursor) -> list[tuple]:
        """Return courses that have a translation for the given language key."""
        cursor.execute(Q.SQL_SEARCH_CURSOS_I18N, (lang, lang))
        return cursor.fetchall()

    @with_cursor
    def search_i18n_value(self, lang: str, term: str, *, cursor) -> list[tuple]:
        """Return courses whose translated name in `lang` matches the term."""
        cursor.execute(Q.SQL_SEARCH_CURSOS_I18N_VALUE, (lang, f"%{term}%"))
        return cursor.fetchall()


# ---------------------------------------------------------------------------
# Matriculas
# ---------------------------------------------------------------------------

class OperacionesMatricula:

    @with_cursor
    def insert_one_enrollment(self, matricula: Matriculas, *, cursor) -> None:
        cursor.execute(
            Q.SQL_INSERT_MATRICULA,
            (matricula.alumno_id, matricula.curso_id, matricula.created_at),
        )

    @with_cursor
    def get_all_enrollments(self, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_GET_ALL_MATRICULAS)
        return cursor.fetchall()

    @with_cursor
    def search_by_extras(self, json_filter: str, *, cursor) -> list[tuple]:
        """Filter matriculas by JSONB containment (@>). Pass a JSON string."""
        cursor.execute(Q.SQL_SEARCH_MATRICULAS_JSONB, (json_filter,))
        return cursor.fetchall()


# ---------------------------------------------------------------------------
# Consultas avanzadas — tema13
# ---------------------------------------------------------------------------

class OperacionesConsultasAvanzadas:

    @with_cursor
    def row_number_top_cursos(self, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_ROW_NUMBER_TOP_CURSOS_POR_MES)
        return cursor.fetchall()

    @with_cursor
    def grouping_sets_matriculas(self, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_GROUPING_SETS_MATRICULAS)
        return cursor.fetchall()

    @with_cursor
    def rollup_matriculas(self, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_ROLLUP_MATRICULAS)
        return cursor.fetchall()

    @with_cursor
    def filter_semestres(self, *, cursor) -> list[tuple]:
        cursor.execute(Q.SQL_FILTER_SEMESTRES)
        return cursor.fetchall()
