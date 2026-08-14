# Mini-REST-API: Note-Taking Web Application
## Overview
Mini-REST-API is a full-stack note-taking application: a Flask JSON API backend and a Next.js frontend, running as two separate servers. Users can register, log in, and manage personal notes (create, view, edit, delete), while administrators have additional privileges to manage user accounts. The application features secure authentication (JWT and CSRF protection), rate limiting, and a PostgreSQL database.

## Features

- **User Authentication:**  
  Secure login and registration with JWT-based authentication and CSRF protection.

- **Note Management:**  
  Users can create, view, edit, and delete notes with a maximum title length of 20 characters.

- **Admin User Management:**  
  Admins can create, view, update, and delete user accounts with role-based access control.

- **Frontend:**  
  Next.js (App Router, TypeScript, Tailwind CSS) with a custom "Ledger" design system — a graph-paper, card-catalog aesthetic rather than a generic dashboard template.

- **Client-Side Validation:**  
  Enforces username (3-20 chars), email format, and strong password requirements (8+ chars, uppercase, lowercase, digit, special character), mirroring the backend's rules.

- **Server-Side Validation:**  
  Uses Marshmallow schemas for API request validation.

- **Security:**  
  - JWT authentication (tokens in httpOnly cookies).  
  - CSRF protection for API requests via a token endpoint the frontend fetches on load.  
  - Rate limiting (10/min for login, 5/min for register, 200/day globally); session-check endpoints are exempted since the frontend calls them on every navigation.  
  - Credentialed CORS for the frontend origin (localhost:3000).


Database: PostgreSQL with migrations managed via Flask-Migrate and Alembic.

## Tech Stack


### Backend:
Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Limiter, Flask-CORS, Flask-RESTful, Flask-Marshmallow, Flask-WTF, psycopg2-binary, python-dotenv, redis, alembic


### Frontend:
Next.js (App Router), TypeScript, Tailwind CSS, next/font (JetBrains Mono + Inter)


### Testing:
pytest


### Package Manager:
uv (backend), npm (frontend)


## Installation
### Prerequisites

- Python &gt;= 3.12
- Node.js and npm
- PostgreSQL (running locally or via a service)
- Redis (for rate limiting)
- uv package manager

### Setup

#### Clone the Repository:
git clone &lt;repository-url&gt;
cd mini-rest-api


#### Backend

Create and activate a virtual environment:
- uv venv
- source .venv/bin/activate  # Linux/Mac
- .venv\Scripts\Activate.ps1  # Windows PowerShell

Install dependencies:
- uv sync

Configure environment variables — create a .env file in the project root:
- DATABASE_URL=postgresql://user:password@localhost:5432/your_database
- SECRET_KEY=your-secret-key
- JWT_SECRET_KEY=your-jwt-secret-key
- REDIS_URL=redis://localhost:6379/0 (optional, works without it if uses default settings)

Initialize the database:
- export FLASK_APP=main.py  # Linux/Mac (use `set` for Windows)
- flask db init  # Initialize migrations (run once)
- flask db migrate -m "Initial migration"
- flask db upgrade

#### Frontend

- cd frontend
- npm install
- Optionally set NEXT_PUBLIC_API_URL if the backend isn't at http://localhost:5000


## Running the Application

Start the backend (from the project root):
- uv run main.py
- or: flask run (needs a .flaskenv file with FLASK_APP=main)

Start the frontend (from `frontend/`):
- npm run dev

The frontend is at http://localhost:3000 (this is what you open in a browser) and talks to the API at http://localhost:5000.

## Usage

### API Endpoints

| Endpoint                 | Method | Description                  | Authentication |
|--------------------------|--------|-------------------------------|----------------|
| /api/v1/csrf-token       | GET    | Get a CSRF token for the session | None        |
| /api/v1/login            | POST   | Authenticate user, return JWT | None           |
| /api/v1/register         | POST   | Register new user             | None           |
| /api/v1/logout           | POST   | Clear the JWT cookie          | None           |
| /api/v1/me               | GET    | Get the current user          | JWT            |
| /api/v1/notes            | GET    | List user's notes             | JWT            |
| /api/v1/notes            | POST   | Create a new note             | JWT            |
| /api/v1/notes/<id>       | GET    | Get note details               | JWT (owner)    |
| /api/v1/notes/<id>       | PATCH  | Update note                    | JWT (owner)    |
| /api/v1/notes/<id>       | DELETE | Delete note                    | JWT (owner)    |
| /api/v1/admin/users      | GET    | List all users                 | JWT (admin)    |
| /api/v1/admin/users      | POST   | Create a user                  | JWT (admin)    |
| /api/v1/admin/users/<id> | GET    | Get user details               | JWT (admin)    |
| /api/v1/admin/users/<id> | PUT    | Update user                    | JWT (admin or self) |
| /api/v1/admin/users/<id> | DELETE | Delete user                    | JWT (admin)    |

### Frontend Routes

| Route          | Description                                |
|----------------|---------------------------------------------|
| /              | Landing page                               |
| /login         | Sign in                                    |
| /register      | Create an account                          |
| /notes         | Notes dashboard (requires authentication)  |
| /notes/new     | Create a note                              |
| /notes/<id>    | View/edit/delete a note                    |
| /admin         | User list (admin-only)                     |
| /admin/new     | Create a user (admin-only)                 |
| /admin/<id>    | View/edit/delete a user (admin-only)       |


## Security

JWT Authentication: Tokens stored in an httpOnly cookie, validated for protected routes.
CSRF Protection: Enabled for API requests; the frontend fetches a token from /api/v1/csrf-token and sends it back as an X-CSRF-Token header on writes.
Rate Limiting: 10/min for /api/v1/login, 5/min for /api/v1/register, 200/day globally, using Redis. /api/v1/me and /api/v1/csrf-token are exempt since the frontend calls them on every navigation.
CORS: Restricted to localhost:3000, with credentials enabled so the JWT cookie is sent cross-origin.

## Known issues / future improvements

- `PUT /api/v1/admin/users/<id>` lets a user edit their own record, including the `status` field — in principle a regular user could self-promote to admin via a direct API call. Not reachable through the frontend (admin pages are gated), but the backend should restrict who can change `status`.
- JWT errors (missing/invalid token) return a generic 500 instead of a 401 across the API.
- The pytest fixture's `SQLALCHEMY_DATABASE_URI` override doesn't take effect before `db.create_all()` runs, so the test suite currently hits whatever `DATABASE_URL` is set at import time instead of the intended in-memory SQLite.
- Implement pagination for large note/user lists.
- Add server-side caching (e.g., Flask-Caching) for API performance.
