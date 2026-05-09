import os

# PostgreSQL connection
PG_HOST     = os.environ.get("DB_HOST",     "localhost")
PG_DB       = os.environ.get("DB_NAME",     "gestorclases")
PG_USER     = os.environ.get("DB_USER",     "postgres")
PG_PASSWORD = os.environ.get("DB_PASSWORD", "")
PG_PORT     = int(os.environ.get("DB_PORT", 5432))

# SQLite auth
SQLITE_PATH = os.environ.get("SQLITE_PATH", "./auth.db")

# Flask server
SERVER_IP   = os.environ.get("SERVER_IP",   "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", 3000))

# Flask templates
TEMPLATE_DIR = os.environ.get("TEMPLATE_DIR", "./templates")

# Pagination
PAGE_SIZE = int(os.environ.get("PAGE_SIZE", 10))
