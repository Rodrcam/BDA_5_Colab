# =============================================================================
# querys.py — ALL SQL queries for the application.
# No SQL strings are defined anywhere else in the codebase.
# Uses psycopg2 parameterised form: %s for positional parameters.
# Literal % SQL operators (pg_trgm) are escaped as %% in Python strings.
# =============================================================================

# ---------------------------------------------------------------------------
# PostgreSQL extensions (tema12)
# ---------------------------------------------------------------------------
SQL_CREATE_EXTENSIONS = [
    "CREATE EXTENSION IF NOT EXISTS unaccent;",
    "CREATE EXTENSION IF NOT EXISTS citext;",
    "CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;",
    "CREATE EXTENSION IF NOT EXISTS btree_gin;",
    "CREATE EXTENSION IF NOT EXISTS pg_trgm;",
]

# ---------------------------------------------------------------------------
# Table DDL
# ---------------------------------------------------------------------------
SQL_CREATE_TABLE_PROFESORES = """
CREATE TABLE IF NOT EXISTS profesores (
    id   uuid PRIMARY KEY,
    nombre text NOT NULL
);
"""

SQL_CREATE_TABLE_ALUMNOS = """
CREATE TABLE IF NOT EXISTS alumnos (
    id     uuid  PRIMARY KEY,
    nombre text  NOT NULL,
    email  citext UNIQUE NOT NULL,
    extras jsonb NOT NULL DEFAULT '{}'::jsonb
);
"""

SQL_CREATE_TABLE_CURSOS = """
CREATE TABLE IF NOT EXISTS cursos (
    id          uuid PRIMARY KEY,
    nombre      text NOT NULL,
    nombre_i18n jsonb NOT NULL DEFAULT '{}'::jsonb,
    nombre_tsv  tsvector GENERATED ALWAYS AS (
                    to_tsvector('spanish', coalesce(nombre, ''))
                ) STORED,
    profesor_id uuid REFERENCES profesores(id)
);
"""

SQL_CREATE_TABLE_MATRICULAS = """
CREATE TABLE IF NOT EXISTS matriculas (
    alumno_id  uuid REFERENCES alumnos(id),
    curso_id   uuid REFERENCES cursos(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    extras     jsonb NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (alumno_id, curso_id)
);
"""

# ---------------------------------------------------------------------------
# Index DDL
# ---------------------------------------------------------------------------
SQL_CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS cursos_nombre_trgm_idx  ON cursos  USING GIN (nombre gin_trgm_ops);",
    "CREATE INDEX IF NOT EXISTS cursos_nombre_tsv_idx   ON cursos  USING GIN (nombre_tsv);",
    "CREATE INDEX IF NOT EXISTS cursos_nombre_i18n_idx  ON cursos  USING GIN (nombre_i18n jsonb_path_ops);",
    "CREATE INDEX IF NOT EXISTS alumnos_extras_idx      ON alumnos USING GIN (extras jsonb_path_ops);",
    "CREATE INDEX IF NOT EXISTS alumnos_nombre_trgm_idx ON alumnos USING GIN (nombre gin_trgm_ops);",
]

# ---------------------------------------------------------------------------
# INSERT queries
# ---------------------------------------------------------------------------
SQL_INSERT_PROFESOR = (
    "INSERT INTO profesores (id, nombre) VALUES (%s, %s)"
)

SQL_INSERT_ALUMNO = (
    "INSERT INTO alumnos (id, nombre, email) VALUES (%s, %s, %s)"
)

# nombre_tsv is GENERATED — do not include in INSERT
SQL_INSERT_CURSO = (
    "INSERT INTO cursos (id, nombre, nombre_i18n, profesor_id)"
    " VALUES (%s, %s, %s::jsonb, %s)"
)

SQL_INSERT_MATRICULA = (
    "INSERT INTO matriculas (alumno_id, curso_id, created_at) VALUES (%s, %s, %s)"
)

# ---------------------------------------------------------------------------
# SELECT — full listings
# ---------------------------------------------------------------------------
SQL_GET_ALL_PROFESORES = (
    "SELECT id, nombre FROM profesores ORDER BY nombre"
)

SQL_GET_ALL_ALUMNOS = (
    "SELECT id, nombre, email FROM alumnos ORDER BY nombre"
)

SQL_GET_ALL_CURSOS = (
    "SELECT c.id, c.nombre, c.nombre_i18n, p.nombre AS profesor"
    "  FROM cursos c"
    "  LEFT JOIN profesores p ON c.profesor_id = p.id"
    " ORDER BY c.nombre"
)

SQL_GET_ALL_MATRICULAS = (
    "SELECT a.nombre, c.nombre, m.created_at"
    "  FROM matriculas m"
    "  JOIN alumnos a ON m.alumno_id = a.id"
    "  JOIN cursos  c ON m.curso_id  = c.id"
)

# ---------------------------------------------------------------------------
# Search — tema12 features
# ---------------------------------------------------------------------------

# ILIKE — case-insensitive pattern match (pass '%term%' as the parameter)
SQL_SEARCH_CURSOS_ILIKE = (
    "SELECT id, nombre, nombre_i18n FROM cursos WHERE nombre ILIKE %s"
)

# Full-text search via tsvector generated column
SQL_SEARCH_CURSOS_FULLTEXT = (
    "SELECT id, nombre, nombre_i18n"
    "  FROM cursos"
    " WHERE nombre_tsv @@ plainto_tsquery('spanish', %s)"
)

# pg_trgm similarity — %% is a literal % in psycopg2 (the trigram operator)
SQL_SEARCH_CURSOS_SIMILARITY = (
    "SELECT id, nombre, nombre_i18n, similarity(nombre, %s) AS sim"
    "  FROM cursos"
    " WHERE nombre %% %s"
    " ORDER BY sim DESC"
    " LIMIT 10"
)

# fuzzystrmatch — Levenshtein distance
SQL_SEARCH_CURSOS_LEVENSHTEIN = (
    "SELECT id, nombre, levenshtein(lower(nombre), lower(%s)) AS dist"
    "  FROM cursos"
    " WHERE levenshtein(lower(nombre), lower(%s)) <= %s"
    " ORDER BY dist"
)

# unaccent — accent-insensitive search on alumnos
SQL_SEARCH_ALUMNOS_UNACCENT = (
    "SELECT id, nombre, email"
    "  FROM alumnos"
    " WHERE unaccent(lower(nombre)) ILIKE unaccent(lower(%s))"
)

# JSONB i18n — list courses that have a translation for a given language key
SQL_SEARCH_CURSOS_I18N = (
    "SELECT id, nombre, nombre_i18n->>%s AS titulo_local"
    "  FROM cursos"
    " WHERE nombre_i18n ? %s"
)

# JSONB i18n — search by translated value (e.g. English name ILIKE ?)
SQL_SEARCH_CURSOS_I18N_VALUE = (
    "SELECT id, nombre, nombre_i18n"
    "  FROM cursos"
    " WHERE nombre_i18n->>%s ILIKE %s"
)

# JSONB extras filter on matriculas (@> containment)
SQL_SEARCH_MATRICULAS_JSONB = (
    "SELECT m.alumno_id, m.curso_id"
    "  FROM matriculas m"
    " WHERE m.extras @> %s::jsonb"
)

# JSONB key existence check on alumnos
SQL_SEARCH_ALUMNOS_JSONB_KEY = (
    "SELECT id, nombre FROM alumnos WHERE extras ? %s"
)

# ---------------------------------------------------------------------------
# SQLite — auth
# ---------------------------------------------------------------------------
SQL_SQLITE_CREATE_USERS = """
CREATE TABLE IF NOT EXISTS usuarios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    nombre        TEXT NOT NULL,
    rol           TEXT NOT NULL DEFAULT 'alumno'
                       CHECK (rol IN ('admin', 'profesor', 'alumno')),
    is_active     INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL
)
"""

SQL_SQLITE_CREATE_INDEXES = [
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios (username)",
    "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_email    ON usuarios (email)",
]

SQL_SQLITE_INSERT_USER = (
    "INSERT OR IGNORE INTO usuarios"
    " (username, email, password_hash, nombre, rol, is_active, created_at)"
    " VALUES (?, ?, ?, ?, ?, 1, ?)"
)

SQL_SQLITE_GET_USER = (
    "SELECT username, password_hash, rol, nombre, is_active"
    "  FROM usuarios WHERE username = ?"
)

# ---------------------------------------------------------------------------
# Utility / audit
# ---------------------------------------------------------------------------
SQL_GET_VERSION = "SELECT version()"

SQL_GET_COUNTS = (
    "SELECT"
    "  (SELECT COUNT(*) FROM alumnos)    AS alumnos,"
    "  (SELECT COUNT(*) FROM profesores) AS profesores,"
    "  (SELECT COUNT(*) FROM cursos)     AS cursos,"
    "  (SELECT COUNT(*) FROM matriculas) AS matriculas"
)

# ---------------------------------------------------------------------------
# Consultas avanzadas — tema13
# ---------------------------------------------------------------------------

# ROW_NUMBER — Top 3 cursos con más matrículas por mes
SQL_ROW_NUMBER_TOP_CURSOS_POR_MES = """
WITH base AS (
    SELECT
        date_trunc('month', m.created_at) AS mes,
        c.nombre                           AS curso,
        COUNT(*)                           AS total_matriculas
    FROM matriculas m
    JOIN cursos c ON m.curso_id = c.id
    GROUP BY 1, 2
)
SELECT mes, curso, total_matriculas, puesto
FROM (
    SELECT *,
           row_number() OVER (PARTITION BY mes ORDER BY total_matriculas DESC) AS puesto
    FROM base
) ranked
WHERE puesto <= 3
ORDER BY mes, puesto;
"""

# GROUPING SETS — Matrículas por (mes, curso), por mes y total global
SQL_GROUPING_SETS_MATRICULAS = """
SELECT
    date_trunc('month', m.created_at) AS mes,
    c.nombre                           AS curso,
    COUNT(*)                           AS total
FROM matriculas m
JOIN cursos c ON m.curso_id = c.id
GROUP BY GROUPING SETS (
    (date_trunc('month', m.created_at), c.nombre),
    (date_trunc('month', m.created_at)),
    ()
)
ORDER BY mes NULLS LAST, curso NULLS LAST;
"""

# ROLLUP — Matrículas por mes y alumno con subtotales por mes y total global
SQL_ROLLUP_MATRICULAS = """
SELECT
    date_trunc('month', m.created_at) AS mes,
    a.nombre                           AS alumno,
    COUNT(*)                           AS total
FROM matriculas m
JOIN alumnos a ON m.alumno_id = a.id
GROUP BY ROLLUP (date_trunc('month', m.created_at), a.nombre)
ORDER BY mes NULLS LAST, alumno NULLS LAST;
"""

# FILTER — Matrículas del 1er semestre vs 2o semestre por alumno
SQL_FILTER_SEMESTRES = """
SELECT
    a.nombre AS alumno,
    COUNT(*) FILTER (WHERE EXTRACT(month FROM m.created_at) BETWEEN 1 AND 6)   AS primer_semestre,
    COUNT(*) FILTER (WHERE EXTRACT(month FROM m.created_at) BETWEEN 7 AND 12)  AS segundo_semestre,
    COUNT(*)                                                                     AS total
FROM matriculas m
JOIN alumnos a ON m.alumno_id = a.id
GROUP BY a.nombre
ORDER BY total DESC, a.nombre;
"""
