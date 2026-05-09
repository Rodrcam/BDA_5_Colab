# Gestor de Clases — BDA Práctica 4

Sistema de gestión académica construido con arquitectura MVC sobre Flask y PostgreSQL, con autenticación en SQLite y pipelines de carga de datos en Apache Airflow.

---

## 1. Requisitos previos

| Herramienta | Versión mínima |
|---|---|
| Python | 3.10+ |
| PostgreSQL | 14+ |
| pip / venv | incluido en Python |
| Apache Airflow | 2.11.0 (opcional, solo para los DAGs) |

Dependencias Python (`requirements.txt`):

```
Flask>=3.0.0
psycopg2-binary>=2.9.9
faker>=24.0.0
apache-airflow==2.11.0
```

---

## 2. Estructura del proyecto

```
GestorClasesBBDDA/
│
├── main.py                   # Punto de entrada (--rs arranca el servidor)
├── app.py                    # Fábrica Flask, registro de blueprints
├── bootstrap_auth.py         # Script auxiliar: crea auth.db sin Airflow
├── database_menu.py          # Menú interactivo de base de datos (CLI)
├── faker_seed.py             # Seed de datos con Faker
├── requirements.txt
│
├── config/
│   ├── database.ini          # Credenciales PostgreSQL (no subir al repo)
│   ├── database.ini.example  # Plantilla de configuración
│   ├── config.py             # Lectura del .ini con ConfigParser
│   └── load.py               # Exporta variables: PG_*, SQLITE_PATH, PAGE_SIZE…
│
├── models/
│   ├── entities.py           # Dataclasses: Alumnos, Profesores, Cursos, Matriculas
│   ├── db/
│   │   ├── decorators.py     # @with_cursor, @with_transactions, @with_sqlite
│   │   ├── psql.py           # Clases ORM: PostgreSQL, OperacionesProfesor…
│   │   ├── sqlite.py         # Clase Sqlite: autenticación sobre auth.db
│   │   ├── querys.py         # Todas las queries SQL (PostgreSQL y SQLite)
│   │   └── transacciones.py  # Demo de transacciones con rollback
│   └── dag/
│       ├── utils.py          # Datos y helpers compartidos entre DAGs
│       ├── dag_psql.py       # DAG Parte A: esquema académico en PostgreSQL
│       └── dag_sqlite.py     # DAG Parte B: usuarios en SQLite
│
├── routes/
│   ├── __init__.py           # Exporta todos los blueprints
│   ├── auth.py               # /auth/login, /auth/logout
│   ├── home.py               # / → dashboard con contadores
│   ├── profesores.py         # /profesores
│   ├── alumnos.py            # /alumnos
│   ├── asignaturas.py        # /asignaturas (≡ cursos)
│   ├── matriculas.py         # /matriculas
│   └── transacciones.py      # /transacciones (demo rollback)
│
├── templates/                # Jinja2, un subdirectorio por módulo
├── static/
│   ├── css/base.css
│   └── js/                   # Un .js por módulo (fetch + modals)
│
└── auth.db                   # Base de datos SQLite (generada en ejecución)
```

---

## 3. Configuración inicial

### 3.1 Clonar e instalar dependencias

```bash
git clone <url-del-repositorio>
cd GestorClasesBBDDA

python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3.2 Configurar la conexión a PostgreSQL

Copia la plantilla y rellena tus credenciales:

```bash
cp config/database.ini.example config/database.ini
```

Edita `config/database.ini`:

```ini
[postgresql]
host=localhost
database=nombre_base_datos
user=usuario
password=contraseña
port=5432

[server]
server_ip=0.0.0.0
server_port=3000
template_dir=./templates

[app]
page_size=10
```

---

## 4. Cómo levantar Apache Airflow

> Solo necesario para ejecutar los DAGs. Si prefieres no usar Airflow, ve directamente al apartado 5 (script alternativo).

### 4.1 Inicializar Airflow (primera vez)

```bash
# Linux / macOS
export AIRFLOW_HOME=$(pwd)/airflow_home

# PowerShell
$env:AIRFLOW_HOME = "$PWD\airflow_home"

airflow db migrate

airflow users create \
    --username admin \
    --password admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
```

### 4.2 Apuntar Airflow a la carpeta de DAGs

En `airflow_home/airflow.cfg`, establece:

```ini
dags_folder = /ruta/absoluta/al/proyecto/models/dag
```

### 4.3 Arrancar los servicios de Airflow

Abre dos terminales:

```bash
# Terminal 1
airflow scheduler

# Terminal 2
airflow webserver --port 8080
```

Accede a `http://localhost:8080` con las credenciales del paso 4.1.

---

## 5. Cómo ejecutar ambos DAGs

### DAG Parte A — Esquema académico PostgreSQL

**ID:** `dag_academico_postgresql`

Crea las tablas `profesores`, `alumnos`, `cursos` y `matriculas` con sus índices, e inserta un dataset mínimo de prueba (10 profesores, 100 alumnos, 20 cursos, 200 matrículas).

**Desde la UI de Airflow:**
1. Ir a la pestaña *DAGs*
2. Activar `dag_academico_postgresql`
3. Pulsar *Trigger DAG* ▶

**Desde la CLI:**
```bash
airflow dags trigger dag_academico_postgresql
```

Secuencia de tareas:
```
comprobar_conexion → crear_esquema → insertar_datos
```

---

### DAG Parte B — Usuarios SQLite

**ID:** `dag_usuarios_sqlite`

Crea `auth.db` con la tabla `usuarios` e inserta los tres usuarios del sistema con contraseñas cifradas (pbkdf2:sha256).

**Desde la UI de Airflow:**
1. Activar `dag_usuarios_sqlite`
2. Pulsar *Trigger DAG* ▶

**Desde la CLI:**
```bash
airflow dags trigger dag_usuarios_sqlite
```

Secuencia de tareas:
```
comprobar_sqlite → crear_tabla_usuarios → insertar_usuarios
```

**Alternativa sin Airflow** — script auxiliar incluido en el proyecto:

```bash
python bootstrap_auth.py
```

Genera `auth.db` directamente en la raíz del proyecto con los mismos tres usuarios.

---

## 6. Cómo arrancar la aplicación MVC

Asegúrate de que:
- PostgreSQL está activo y accesible con las credenciales de `config/database.ini`
- `auth.db` existe (ejecutado el DAG Parte B o `bootstrap_auth.py`)

```bash
python main.py --rs
```

La aplicación estará disponible en: **`http://localhost:3000`**

El puerto puede modificarse en `config/database.ini` → sección `[server]`.

---

## 7. Usuarios del sistema

Al acceder a la aplicación se solicita inicio de sesión. Los usuarios disponibles son:

| Usuario | Contraseña | Rol |
|---|---|---|
| `admin` | `Admin1234!` | Administrador |
| `profesor` | `Profesor1234!` | Profesor |
| `alumno` | `Alumno1234!` | Alumno |

Estos usuarios se crean mediante el DAG Parte B o con `python bootstrap_auth.py`.

---

## 8. Módulos disponibles

| Ruta | Descripción |
|---|---|
| `/profesores` | Listado y detalle de docentes |
| `/alumnos` | Registro de estudiantes |
| `/asignaturas` | Catálogo de asignaturas (equivalente a cursos) |
| `/matriculas` | Inscripciones alumno–asignatura |
| `/transacciones` | Demo interactiva de transacciones con rollback |
| `/auth/login` | Inicio de sesión |
| `/auth/logout` | Cierre de sesión |
