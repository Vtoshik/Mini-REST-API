from marshmallow import Schema, fields, validate, ValidationError, post_load, EXCLUDE
from marshmallow.validate import Length, Email, Regexp

PASSWORD_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&_]{8,}$'
PASSWORD_ERROR = "Password must be 8+ characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character from @, $, !, %, *, ?, &, _"

class UserRegisterSchema(Schema):
    username  = fields.Str(required=True, validate=Length(min=3, max=20, error="Username 3-20 chars"))
    email = fields.Email(required=True, validate=Length(max=255, error="Email too long"))
    password = fields.Str(required=True, validate=Regexp(PASSWORD_REGEX, error=PASSWORD_ERROR))

    class Meta:
        unknown = EXCLUDE

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=Length(min=3, max=20, error="Username 3-20 chars"))
    password = fields.Str(required=True)

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=Length(min=3, max=20))
    email = fields.Str(required=True, validate=Email())
    status = fields.Str(validate=validate.OneOf(["user", "admin"]))
    created_at = fields.DateTime(dump_only=True)

class UserUpdateSchema(Schema):
    """Admin-only update: username/email/status. Passwords go through the
    reset-token flow (AdminPasswordReset/PasswordReset) instead of being set
    directly here, so an admin never handles another user's plaintext password."""
    username = fields.Str(validate=Length(min=3, max=20, error="Username 3-20 chars"))
    email = fields.Email(validate=Length(max=255, error="Email too long"))
    status = fields.Str(validate=validate.OneOf(["user", "admin"], error="Invalid status"))

class SelfUpdateSchema(Schema):
    """Self-service update via PUT /api/v1/me: username/email only."""
    username = fields.Str(validate=Length(min=3, max=20, error="Username 3-20 chars"))
    email = fields.Email(validate=Length(max=255, error="Email too long"))

class PasswordChangeSchema(Schema):
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=Regexp(PASSWORD_REGEX, error=PASSWORD_ERROR))

class PasswordResetSchema(Schema):
    token = fields.Str(required=True)
    password = fields.Str(required=True, validate=Regexp(PASSWORD_REGEX, error=PASSWORD_ERROR))

class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=Length(max=20, error="Title max 20 chars"))
    content = fields.Str()
    category = fields.Str(allow_none=True)
    pinned = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True, allow_none=True)


class NoteCreateSchema(Schema):
    title = fields.Str(
        required=True,
        validate=[
            Length(max=20, error="Title max 20 chars"),
            Regexp(r'^\S.*\S$', error="Title cannot be empty or whitespace-only")
        ]
    )
    content = fields.Str(required=False, allow_none=True, validate=Length(max=20000, error="Content max 20000 chars"))
    category = fields.Str(required=False, allow_none=True, validate=Length(max=30, error="Category max 30 chars"))

    @post_load
    def strip_whitespace(self, data, **kwargs):
        if data.get('title'):
            data['title'] = data['title'].strip()
        if data.get('content'):
            data['content'] = data['content'].strip()
        if data.get('category'):
            data['category'] = data['category'].strip()
        return data

    class Meta:
        unknown = EXCLUDE # Ignore unknown fields like user_id

class NoteUpdateSchema(Schema):
    title = fields.Str(
        validate=[
            Length(max=20, error="Title max 20 chars"),
            Regexp(r'^\S.*\S$', error="Title cannot be empty or whitespace-only")
        ]
    )
    content = fields.Str(allow_none=True, validate=Length(max=20000, error="Content max 20000 chars"))
    category = fields.Str(allow_none=True, validate=Length(max=30, error="Category max 30 chars"))
    pinned = fields.Bool()

    @post_load
    def strip_whitespace(self, data, **kwargs):
        if data.get('title'):
            data['title'] = data['title'].strip()
        if data.get('content'):
            data['content'] = data['content'].strip()
        if data.get('category'):
            data['category'] = data['category'].strip()
        return data

    class Meta:
        unknown = EXCLUDE
