# Mini-REST API Project

## Description
This project is a mini REST API on Flask using PostgreSQL for data storage.  
It includes basic authentication, user and note models, and database migration management via Alembic/Flask-Migrate.

---

## Installation and launch

### Setting up the virtual environment and activation
The project manager [uv](https://github.com/astral-sh/uv) is used.

uv venv
source .venv/bin/activate # For Linux/Mac

.venv\Scripts\Activate.ps1 # For Windows PowerShell

### Installing dependencies
To install all the necessary libraries, use the command:
uv sync

---

## Libraries used

| Library             | Description                                 |
|---------------------|---------------------------------------------|
| `flask`             | Web framework                               |
| `flask_sqlalchemy`  | ORM for working with the database via Flask |
| `psycopg2-binary`   | PostgreSQL driver                           |
| `flask-migrate`     | Database migrations (Alembic wrapper)       |
| `python-dotenv`     | Loading environment variables (.env)        |

---

## Running the project

After installing the dependencies, the server is started with the command:
uv run main.py
or
flask run

Make sure that your directory contains a `.env` file with the correct `DATABASE_URL`, for example:
DATABASE_URL=postgresql://user:password@localhost:5432/your_database

---

## Working with database migrations

To manage migrations, use Flask CLI:
export FLASK_APP=main.py # Linux/Mac, for Windows options are different
flask db init # Initialise migrations (once)
flask db migrate -m ‘description of changes’ # Create migration
flask db upgrade # Apply migration

