# openapi.py
# Builds the OpenAPI spec served at /api/v1/openapi.json (see main.py) and
# rendered as Swagger UI at /api/v1/docs. Paths are hand-written — the API's
# JWT-cookie + X-CSRF-Token auth isn't something flask-restful introspection
# would infer correctly — but request/response bodies reuse the Marshmallow
# schemas in schemas.py via apispec's Marshmallow plugin, so field
# definitions aren't duplicated by hand.
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin

from schemas import (
    UserRegisterSchema, LoginSchema, UserSchema, UserUpdateSchema,
    SelfUpdateSchema, PasswordChangeSchema, PasswordResetSchema, EmailVerificationSchema,
    NoteSchema, NoteCreateSchema, NoteUpdateSchema,
)

CSRF_NOTE = (
    "Requires an `X-CSRF-Token` header (fetch one from `GET /api/v1/csrf-token` first)."
)

spec = APISpec(
    title="Mini-REST-API",
    version="1.0.0",
    openapi_version="3.0.3",
    info={
        "description": (
            "Note-taking API: JWT auth (cookie or Authorization header), "
            "CSRF-protected writes, per-user notes with categories/pinning/trash, "
            "and admin user management."
        ),
    },
    plugins=[MarshmallowPlugin()],
)

spec.components.security_scheme(
    "cookieAuth", {"type": "apiKey", "in": "cookie", "name": "access_token_cookie"}
)
spec.components.security_scheme(
    "bearerAuth", {"type": "http", "scheme": "bearer"}
)
JWT_AUTH = [{"cookieAuth": []}, {"bearerAuth": []}]

for name, schema in [
    ("UserRegister", UserRegisterSchema),
    ("Login", LoginSchema),
    ("User", UserSchema),
    ("UserUpdate", UserUpdateSchema),
    ("SelfUpdate", SelfUpdateSchema),
    ("PasswordChange", PasswordChangeSchema),
    ("PasswordReset", PasswordResetSchema),
    ("EmailVerification", EmailVerificationSchema),
    ("Note", NoteSchema),
    ("NoteCreate", NoteCreateSchema),
    ("NoteUpdate", NoteUpdateSchema),
]:
    spec.components.schema(name, schema=schema)


def _json(schema_name=None, description=""):
    body = {"description": description}
    if schema_name:
        body["content"] = {"application/json": {"schema": schema_name}}
    return body


PAGINATION_PROPS = {
    "page": {"type": "integer"},
    "per_page": {"type": "integer"},
    "total": {"type": "integer"},
    "total_pages": {"type": "integer"},
}

PAGE_QUERY_PARAMS = [
    {"in": "query", "name": "page", "schema": {"type": "integer", "default": 1}},
    {"in": "query", "name": "per_page", "schema": {"type": "integer", "default": 20, "maximum": 100}},
]


def _paginated(item_schema):
    return {
        "type": "object",
        "properties": {
            "data": {"type": "array", "items": item_schema},
            "pagination": {"type": "object", "properties": PAGINATION_PROPS},
        },
    }


spec.path(
    path="/api/v1/csrf-token",
    operations={
        "get": {
            "summary": "Get a CSRF token for the current session",
            "tags": ["Auth"],
            "responses": {200: _json(description="Token issued")},
        }
    },
)

spec.path(
    path="/api/v1/register",
    operations={
        "post": {
            "summary": "Register a new user",
            "tags": ["Auth"],
            "requestBody": {"content": {"application/json": {"schema": UserRegisterSchema}}},
            "description": (
                "No email service is configured, so the response includes a verify_token/"
                "verify_path directly rather than emailing it. The account can't log in until "
                "POST /api/v1/verify-email is called with that token."
            ),
            "responses": {
                201: _json(description="User created (unverified)"),
                400: _json(description="Validation error or username/email taken"),
            },
        }
    },
)

spec.path(
    path="/api/v1/verify-email",
    operations={
        "post": {
            "summary": "Verify an email address with a registration token",
            "tags": ["Auth"],
            "requestBody": {"content": {"application/json": {"schema": EmailVerificationSchema}}},
            "responses": {
                200: _json(description="Email verified"),
                400: _json(description="Token invalid, expired, or already used"),
            },
        }
    },
)

spec.path(
    path="/api/v1/login",
    operations={
        "post": {
            "summary": "Authenticate and receive a JWT (set as an httpOnly cookie)",
            "tags": ["Auth"],
            "requestBody": {"content": {"application/json": {"schema": LoginSchema}}},
            "responses": {
                200: _json(description="Login successful"),
                401: _json(description="Invalid credentials"),
                403: _json(description="Email not yet verified"),
                423: _json(description="Account temporarily locked after too many failed attempts"),
            },
        }
    },
)

spec.path(
    path="/api/v1/logout",
    operations={
        "post": {
            "summary": "Clear the JWT cookie",
            "tags": ["Auth"],
            "responses": {200: _json(description="Logout successful")},
        }
    },
)

spec.path(
    path="/api/v1/me",
    operations={
        "get": {
            "summary": "Get the current user",
            "tags": ["Account"],
            "security": JWT_AUTH,
            "responses": {200: _json("User", "Current user"), 401: _json(description="Authentication required")},
        },
        "put": {
            "summary": "Update own username/email",
            "tags": ["Account"],
            "security": JWT_AUTH,
            "description": CSRF_NOTE,
            "requestBody": {"content": {"application/json": {"schema": SelfUpdateSchema}}},
            "responses": {
                200: _json(description="Profile updated"),
                400: _json(description="Validation error or username/email taken"),
            },
        },
    },
)

spec.path(
    path="/api/v1/me/password",
    operations={
        "post": {
            "summary": "Change own password",
            "tags": ["Account"],
            "security": JWT_AUTH,
            "description": f"Requires the current password. {CSRF_NOTE}",
            "requestBody": {"content": {"application/json": {"schema": PasswordChangeSchema}}},
            "responses": {
                200: _json(description="Password updated"),
                400: _json(description="Current password incorrect, or validation error"),
            },
        }
    },
)

spec.path(
    path="/api/v1/reset-password",
    operations={
        "post": {
            "summary": "Complete a password reset with a token",
            "tags": ["Account"],
            "description": CSRF_NOTE,
            "requestBody": {"content": {"application/json": {"schema": PasswordResetSchema}}},
            "responses": {
                200: _json(description="Password reset successful"),
                400: _json(description="Token invalid, expired, or already used"),
            },
        }
    },
)

spec.path(
    path="/api/v1/notes",
    operations={
        "get": {
            "summary": "List the current user's active (non-trashed) notes",
            "tags": ["Notes"],
            "security": JWT_AUTH,
            "parameters": PAGE_QUERY_PARAMS,
            "responses": {200: {"description": "Paginated notes", "content": {"application/json": {"schema": _paginated(NoteSchema)}}}},
        },
        "post": {
            "summary": "Create a note",
            "tags": ["Notes"],
            "security": JWT_AUTH,
            "description": CSRF_NOTE,
            "requestBody": {"content": {"application/json": {"schema": NoteCreateSchema}}},
            "responses": {
                201: _json(description="Note created"),
                400: _json(description="Validation error or duplicate active title"),
            },
        },
    },
)

spec.path(
    path="/api/v1/notes/trash",
    operations={
        "get": {
            "summary": "List the current user's trashed notes",
            "tags": ["Notes"],
            "security": JWT_AUTH,
            "parameters": PAGE_QUERY_PARAMS,
            "responses": {200: {"description": "Paginated trashed notes", "content": {"application/json": {"schema": _paginated(NoteSchema)}}}},
        }
    },
)

spec.path(
    path="/api/v1/notes/{note_id}",
    operations={
        "get": {
            "summary": "Get note details",
            "tags": ["Notes"],
            "security": JWT_AUTH,
            "parameters": [{"in": "path", "name": "note_id", "required": True, "schema": {"type": "integer"}}],
            "responses": {200: _json("Note"), 403: _json(description="Not your note"), 404: _json(description="Not found or trashed")},
        },
        "patch": {
            "summary": "Update title/content/category/pinned",
            "tags": ["Notes"],
            "security": JWT_AUTH,
            "description": CSRF_NOTE,
            "parameters": [{"in": "path", "name": "note_id", "required": True, "schema": {"type": "integer"}}],
            "requestBody": {"content": {"application/json": {"schema": NoteUpdateSchema}}},
            "responses": {200: _json(description="Note updated"), 400: _json(description="Validation error or duplicate active title")},
        },
        "delete": {
            "summary": "Move a note to trash",
            "tags": ["Notes"],
            "security": JWT_AUTH,
            "description": CSRF_NOTE,
            "parameters": [{"in": "path", "name": "note_id", "required": True, "schema": {"type": "integer"}}],
            "responses": {200: _json(description="Note moved to trash")},
        },
    },
)

spec.path(
    path="/api/v1/notes/{note_id}/restore",
    operations={
        "post": {
            "summary": "Restore a trashed note",
            "tags": ["Notes"],
            "security": JWT_AUTH,
            "description": CSRF_NOTE,
            "parameters": [{"in": "path", "name": "note_id", "required": True, "schema": {"type": "integer"}}],
            "responses": {
                200: _json(description="Note restored"),
                400: _json(description="Title now conflicts with an active note"),
                404: _json(description="Not found or not trashed"),
            },
        }
    },
)

spec.path(
    path="/api/v1/notes/{note_id}/permanent",
    operations={
        "delete": {
            "summary": "Permanently delete a trashed note",
            "tags": ["Notes"],
            "security": JWT_AUTH,
            "description": f"Only allowed once a note is already in trash. {CSRF_NOTE}",
            "parameters": [{"in": "path", "name": "note_id", "required": True, "schema": {"type": "integer"}}],
            "responses": {200: _json(description="Permanently deleted"), 404: _json(description="Not found or not trashed")},
        }
    },
)

spec.path(
    path="/api/v1/admin/users",
    operations={
        "get": {
            "summary": "List all users",
            "tags": ["Admin"],
            "security": JWT_AUTH,
            "parameters": PAGE_QUERY_PARAMS,
            "responses": {200: {"description": "Paginated users", "content": {"application/json": {"schema": _paginated(UserSchema)}}}, 403: _json(description="Admin access required")},
        },
        "post": {
            "summary": "Create a user",
            "tags": ["Admin"],
            "security": JWT_AUTH,
            "description": CSRF_NOTE,
            "requestBody": {"content": {"application/json": {"schema": UserRegisterSchema}}},
            "responses": {201: _json(description="User created"), 403: _json(description="Admin access required")},
        },
    },
)

spec.path(
    path="/api/v1/admin/users/{user_id}",
    operations={
        "get": {
            "summary": "Get user details",
            "tags": ["Admin"],
            "security": JWT_AUTH,
            "parameters": [{"in": "path", "name": "user_id", "required": True, "schema": {"type": "integer"}}],
            "responses": {200: _json("User"), 403: _json(description="Admin access required")},
        },
        "put": {
            "summary": "Update username/email/status",
            "tags": ["Admin"],
            "security": JWT_AUTH,
            "description": f"Self can update username/email; only an admin can change status. {CSRF_NOTE}",
            "parameters": [{"in": "path", "name": "user_id", "required": True, "schema": {"type": "integer"}}],
            "requestBody": {"content": {"application/json": {"schema": UserUpdateSchema}}},
            "responses": {200: _json(description="User updated"), 403: _json(description="Forbidden")},
        },
        "delete": {
            "summary": "Delete a user",
            "tags": ["Admin"],
            "security": JWT_AUTH,
            "description": CSRF_NOTE,
            "parameters": [{"in": "path", "name": "user_id", "required": True, "schema": {"type": "integer"}}],
            "responses": {200: _json(description="User deleted"), 403: _json(description="Admin access required")},
        },
    },
)

spec.path(
    path="/api/v1/admin/users/{user_id}/reset-password",
    operations={
        "post": {
            "summary": "Create a password reset link for a user",
            "tags": ["Admin"],
            "security": JWT_AUTH,
            "description": f"Admin-only. Returns a one-time reset token/path — no email service is configured, so share the link with the user manually. {CSRF_NOTE}",
            "parameters": [{"in": "path", "name": "user_id", "required": True, "schema": {"type": "integer"}}],
            "responses": {201: _json(description="Reset token created"), 403: _json(description="Admin access required")},
        }
    },
)
