from marshmallow import Schema, fields, validate, ValidationError, post_load, EXCLUDE
from marshmallow.validate import Length, Email, Regexp

class UserRegisterSchema(Schema):
    username  = fields.Str(required=True, validate=Length(min=3, max=20, error="Username 3-20 chars"))
    email = fields.Email(required=True, validate=Length(max=255, error="Email too long"))
    password = fields.Str(required=True, 
        validate=Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&]{8,}$',
            error="Password must be 8+ characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character from @, $, !, %, *, ?, &, _"
        )
    )

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=Length(min=3, max=20, error="Username 3-20 chars"))
    password = fields.Str(required=True, validate=Length(min=6, error="Password minimum 8 chars"))

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=Length(min=3, max=20))
    email = fields.Str(required=True, validate=Email())
    status = fields.Str(validate=validate.OneOf(["user", "admin"]))
    created_at = fields.DateTime(dump_only=True)

class UserUpdateSchema(Schema):
    username = fields.Str(validate=Length(min=3, max=20, error="Username 3-20 chars"))
    email = fields.Email(validate=Length(max=255, error="Email too long"))
    password = fields.Str(
        validate=Regexp(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&_])[A-Za-z\d@$!%*?&]{8,}$',
            error="Password must be 8+ characters, including at least one uppercase letter, one lowercase letter, one digit, and one special character"
        )
    )
    status = fields.Str(validate=validate.OneOf(["user", "admin"], error="Invalid status"))

class NoteSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=Length(max=20, error="Title max 20 chars"))
    content = fields.Str()
    created_at = fields.DateTime(dump_only=True)


class NoteCreateSchema(Schema):
    title = fields.Str(
        required=True,
        validate=[
            Length(max=20, error="Title max 20 chars"),
            Regexp(r'^\S.*\S$', error="Title cannot be empty or whitespace-only")
        ]
    )
    content = fields.Str(required=False, allow_none=True)

    @post_load
    def strip_whitespace(self, data, **kwargs):
        if data.get('title'):
            data['title'] = data['title'].strip()
        if data.get('content'):
            data['content'] = data['content'].strip()
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
    content = fields.Str(allow_none=True)

    @post_load
    def strip_whitespace(self, data, **kwargs):
        if data.get('title'):
            data['title'] = data['title'].strip()
        if data.get('content'):
            data['content'] = data['content'].strip()
        return data

    class Meta:
        unknown = EXCLUDE
