import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime

conn = sqlite3.connect('auth.db')
cur  = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    nombre TEXT NOT NULL,
    rol TEXT NOT NULL DEFAULT 'alumno' CHECK (rol IN ('admin','profesor','alumno')),
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
)""")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios (username)")
cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios (email)")

for username, email, pwd, nombre, rol in [
    ("admin",    "admin@academico.es",    "Admin1234!",    "Administrador del Sistema", "admin"),
    ("profesor", "profesor@academico.es", "Profesor1234!", "Profesor Demo",             "profesor"),
    ("alumno",   "alumno@academico.es",   "Alumno1234!",   "Alumno Demo",               "alumno"),
]:
    cur.execute("SELECT id FROM usuarios WHERE username=?", (username,))
    if cur.fetchone():
        print(f"[SKIP] {username}")
        continue
    cur.execute(
        "INSERT INTO usuarios (username,email,password_hash,nombre,rol,is_active,created_at) VALUES (?,?,?,?,?,1,?)",
        (username, email, generate_password_hash(pwd, method="pbkdf2:sha256"), nombre, rol, datetime.utcnow().isoformat())
    )
    print(f"[OK] {username} ({rol})")

conn.commit()
conn.close()
print("auth.db listo.")
