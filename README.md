# Mini-REST-API: Note-Taking Web Application
## Overview
Mini-REST-API is a full-stack web application built with Flask, providing a RESTful API and a responsive user interface with note-taking and user management. Users can register, log in, and manage personal notes (create, view, edit, delete), while administrators have additional privileges to manage user accounts. The application features secure authentication (JWT and CSRF protection), rate limiting, a PostgreSQL database.
## Features

- **User Authentication:**  
  Secure login and registration with JWT-based authentication and CSRF protection.

- **Note Management:**  
  Users can create, view, edit, and delete notes with a maximum title length of 20 characters.

- **Admin User Management:**  
  Admins can create, view, update, and delete user accounts with role-based access control.

- **Responsive UI:**  
  Modern, animated interface with password toggle functionality, dynamic dashboards, and editable fields.

- **Client-Side Validation:**  
  Enforces username (3-20 chars), email format, and strong password requirements (8+ chars, uppercase, lowercase, digit, special character).

- **Server-Side Validation:**  
  Uses Marshmallow schemas for API requests and Flask-WTF for form validation.

- **Dynamic Dashboards:**  
  Displays notes (users) or users (admins) in a table with view and delete options.

- **Error Handling:**  
  Client-side error notifications and server-side validation feedback.

- **Security:**  
  - JWT authentication (tokens in cookies/headers).  
  - CSRF protection for forms and API requests.  
  - Rate limiting (10/min for login, 5/min for register, 200/day globally).  
  - CORS for specific origins (localhost:3000, localhost:5000).


Database: PostgreSQL with migrations managed via Flask-Migrate and Alembic.

## Tech Stack


### Backend:
Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, Flask-Limiter, Flask-CORS, Flask-RESTful, Flask-Marshmallow, Flask-WTF, psycopg2-binary, python-dotenv, redis, alembic


### Frontend:
Jinja2 templates, custom CSS, vanilla JavaScript, Google Fonts (Roboto), Font Awesome


### Testing:
pytest


### Package Manager:
uv


## Installation
### Prerequisites

- Python &gt;= 3.12
- PostgreSQL (running locally or via a service)
- Redis (for rate limiting)
- uv package manager

### Setup

#### Clone the Repository:
git clone &lt;repository-url&gt;
cd mini-rest-api


#### Create and Activate Virtual Environment:
uv venv
- source .venv/bin/activate  # Linux/Mac
- .venv\Scripts\Activate.ps1  # Windows PowerShell


#### Install Dependencies:
uv sync


##### Configure Environment Variables: 
Create a .env file in the project root with the following:
- DATABASE_URL=postgresql://user:password@localhost:5432/your_database
- SECRET_KEY=your-secret-key
- JWT_SECRET_KEY=your-jwt-secret-key
- REDIS_URL=redis://localhost:6379/0 (optional, works without it if uses default settings)


Initialize Database:
- export FLASK_APP=main.py  # Linux/Mac (use `set` for Windows)
- flask db init  # Initialize migrations (run once)
- flask db migrate -m "Initial migration"
- flask db upgrade



## Running the Application
Start the local server with:
uv run main.py

or
flask run (you need to have .flaskenv file with parameter FLASK_APP=main)

The application will be available at http://localhost:5000.
## Usage

### User Routes

| Route           | Method | Description                   |
|-----------------|--------|-------------------------------|
| /login          | GET    | Render login page             |
| /register       | GET    | Render registration page      |
| /               | GET    | View user notes (requires authentication) |
| /add_note       | GET    | Create a new note             |
| /note/<id>      | GET    | View/edit note details        |
| /logout         | GET    | Clear session and redirect to login |


### Admin Routes

| Route             | Method | Description              |
|-------------------|--------|--------------------------|
| /admin/           | GET    | View all users (admin-only) |
| /admin/add_data   | GET    | Create a new user         |
| /admin/user/<id>  | GET    | View/edit user details    |

### API Endpoints

| Endpoint                 | Method | Description           | Authentication |
|--------------------------|--------|-----------------------|----------------|
| /api/v1/login            | POST   | Authenticate user, return JWT | None           |
| /api/v1/register         | POST   | Register new user      | None           |
| /api/v1/notes            | GET    | List user’s notes      | JWT            |
| /api/v1/notes            | POST   | Create a new note      | JWT            |
| /api/v1/notes/<id>       | GET    | Get note details       | JWT (owner)    |
| /api/v1/notes/<id>       | PATCH  | Update note            | JWT (owner)    |
| /api/v1/notes/<id>       | DELETE | Delete note            | JWT (owner)    |
| /api/v1/admin/users      | GET    | List all users         | JWT (admin)    |
| /api/v1/admin/users/<id> | GET    | Get user details       | JWT (admin)    |
| /api/v1/admin/users/<id> | PUT    | Update user            | JWT (admin)    |
| /api/v1/admin/users/<id> | DELETE | Delete user            | JWT (admin)    |


## Security

JWT Authentication: Tokens stored in cookies/headers, validated for protected routes.
CSRF Protection: Enabled for forms and API requests via Flask-WTF.
Rate Limiting: 10/min for /api/v1/login, 5/min for /api/v1/register, 200/day globally, using Redis.
CORS: Restricted to localhost:3000 and localhost:5000.

## Future Improvements

Implement pagination for large note/user lists.
Standardize error handling with consistent notifications.
Replace inline onclick with event delegation for better maintainability.
Add server-side caching (e.g., Flask-Caching) for API performance.
Resolve password validation inconsistency.
Add unit tests using pytest.
