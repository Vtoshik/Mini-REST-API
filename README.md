# Mini-REST-API: Note-Taking Web Application

[![CI](https://github.com/Vtoshik/Mini-REST-API/actions/workflows/ci.yml/badge.svg)](https://github.com/Vtoshik/Mini-REST-API/actions/workflows/ci.yml)

## Overview
Mini-REST-API is a full-stack note-taking application: a Flask JSON API backend and a Next.js frontend, running as two separate servers. Users can register, log in, and manage personal notes (create, view, edit, delete), while administrators have additional privileges to manage user accounts. The application features secure authentication (JWT and CSRF protection), rate limiting, and a PostgreSQL database.

## Features

- **User Authentication:**  
  Secure login and registration with JWT-based authentication and CSRF protection.

- **Note Management:**  
  Users can create, view, edit, categorize, and pin notes (title max 20 characters). Deleting moves a note to trash, where it can be restored or permanently deleted. Notes can be searched and filtered by category.

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
Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Limiter, Flask-CORS, Flask-RESTful, Flask-Marshmallow, Flask-WTF, psycopg2-binary, python-dotenv, redis, alembic, apispec, flask-swagger-ui


### Frontend:
Next.js (App Router), TypeScript, Tailwind CSS, next/font (JetBrains Mono + Inter)


### Testing:
pytest (backend), Vitest + React Testing Library (frontend)


### Package Manager:
uv (backend), npm (frontend)


## Quick start with Docker Compose

The fastest way to get everything running locally: `docker compose up` from the project root. This builds and starts Postgres, Redis, the Flask API (auto-applies migrations and seeds demo data on startup — see `flask seed-db` below for the accounts it creates), and the Next.js frontend, all wired together with hot reload against your local source. Frontend at `http://localhost:3000`, API at `http://localhost:5000`. It's a dev setup (hot-reloading dev servers, not a production build) — see `Dockerfile` / `frontend/Dockerfile` / `docker-compose.yml` if you want the details.

If you'd rather run things natively (or don't have Docker), the manual setup below covers both.

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

Optionally seed demo data (admin/demo/empty accounts, demo has 15 sample notes for testing search/filter):
- flask seed-db

Periodically purge used/expired password reset tokens (safe to run on a schedule, e.g. a daily cron):
- flask cleanup-tokens

#### Frontend

- cd frontend
- npm install
- Optionally set NEXT_PUBLIC_API_URL if the backend isn't at http://localhost:5000
- npm run test to run the frontend test suite (Vitest + React Testing Library)


## Running the Application

Start the backend (from the project root):
- uv run main.py
- or: flask run (needs a .flaskenv file with FLASK_APP=main)

Start the frontend (from `frontend/`):
- npm run dev

The frontend is at http://localhost:3000 (this is what you open in a browser) and talks to the API at http://localhost:5000.

## Usage

### API Documentation

Interactive Swagger UI at http://localhost:5000/api/v1/docs (raw spec at `/api/v1/openapi.json`). The endpoint table below is a quick-scan reference; Swagger UI has the full request/response schemas and lets you try requests directly.

### API Endpoints

| Endpoint                 | Method | Description                  | Authentication |
|--------------------------|--------|-------------------------------|----------------|
| /api/v1/csrf-token       | GET    | Get a CSRF token for the session | None        |
| /api/v1/login            | POST   | Authenticate user, return JWT | None           |
| /api/v1/register         | POST   | Register new user (returns a verification link — no email service configured) | None |
| /api/v1/verify-email     | POST   | Verify an email address with a registration token | None |
| /api/v1/logout           | POST   | Clear the JWT cookie          | None           |
| /api/v1/me               | GET    | Get the current user          | JWT            |
| /api/v1/me               | PUT    | Update own username/email     | JWT            |
| /api/v1/me/password      | POST   | Change own password (requires current password) | JWT |
| /api/v1/reset-password   | POST   | Complete a password reset with a token | None   |
| /api/v1/notes            | GET    | List user's active notes       | JWT            |
| /api/v1/notes            | POST   | Create a new note (title, content, category) | JWT |
| /api/v1/notes/<id>       | GET    | Get note details (404 if trashed) | JWT (owner) |
| /api/v1/notes/<id>       | PATCH  | Update note (title/content/category/pinned) | JWT (owner) |
| /api/v1/notes/<id>       | DELETE | Move note to trash              | JWT (owner)    |
| /api/v1/notes/trash      | GET    | List trashed notes             | JWT            |
| /api/v1/notes/<id>/restore | POST | Restore a trashed note        | JWT (owner)    |
| /api/v1/notes/<id>/permanent | DELETE | Permanently delete a trashed note | JWT (owner) |
| /api/v1/admin/users      | GET    | List all users                 | JWT (admin)    |
| /api/v1/admin/users      | POST   | Create a user                  | JWT (admin)    |
| /api/v1/admin/users/<id> | GET    | Get user details               | JWT (admin)    |
| /api/v1/admin/users/<id> | PUT    | Update username/email/status   | JWT (admin or self for username/email; admin only for status) |
| /api/v1/admin/users/<id> | DELETE | Delete user                    | JWT (admin)    |
| /api/v1/admin/users/<id>/reset-password | POST | Create a password reset link for a user | JWT (admin) |

### Frontend Routes

| Route          | Description                                |
|----------------|---------------------------------------------|
| /              | Landing page                               |
| /login         | Sign in                                    |
| /register      | Create an account                          |
| /notes         | Notes dashboard (requires authentication)  |
| /notes/new     | Create a note                              |
| /notes/<id>    | View/edit a note, pin/unpin, move to trash |
| /notes/trash   | Restore or permanently delete trashed notes |
| /account       | Self-service profile and password change (requires authentication) |
| /admin         | User list (admin-only)                     |
| /admin/new     | Create a user (admin-only)                 |
| /admin/<id>    | View/edit/delete a user (admin-only)       |
| /reset-password/<token> | Complete a password reset (public)   |
| /verify-email/<token> | Verify a new account's email (public)  |


## Security

JWT Authentication: Tokens stored in an httpOnly cookie, validated for protected routes.
CSRF Protection: Enabled for API requests; the frontend fetches a token from /api/v1/csrf-token and sends it back as an X-CSRF-Token header on writes.
Rate Limiting: 10/min for /api/v1/login, 5/min for /api/v1/register, 200/day globally (Redis-backed if REDIS_URL is set, otherwise falls back to in-memory storage). /api/v1/me and /api/v1/csrf-token are exempt since the frontend calls them on every navigation.
Account Lockout: after 5 failed login attempts for a given account, it's locked for 15 minutes (returns 423), independent of the IP-based rate limit above.
Email Verification: new accounts can't log in until their email is verified. Since no email service is configured, POST /api/v1/register returns the verification link directly instead of emailing it — a real deployment would email it.
CORS: Restricted to localhost:3000, with credentials enabled so the JWT cookie is sent cross-origin.

## Future improvements

- Add server-side caching (e.g., Flask-Caching) for API performance.

## License

MIT — see [LICENSE](LICENSE).
