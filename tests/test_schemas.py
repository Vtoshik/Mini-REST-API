import pytest
from marshmallow import ValidationError

from schemas import (
    UserRegisterSchema, LoginSchema, NoteCreateSchema, NoteUpdateSchema,
    PasswordChangeSchema, PasswordResetSchema, SelfUpdateSchema, UserUpdateSchema,
)


@pytest.mark.parametrize(
    "password",
    [
        "short1!",       # too short
        "alllowercase1!",  # no uppercase
        "ALLUPPERCASE1!",  # no lowercase
        "NoDigitsHere!",   # no digit
        "NoSpecial1234",   # no special char
    ],
)
def test_register_schema_rejects_weak_passwords(password):
    schema = UserRegisterSchema()
    with pytest.raises(ValidationError):
        schema.load({"username": "valid", "email": "a@example.com", "password": password})


def test_register_schema_accepts_strong_password():
    schema = UserRegisterSchema()
    data = schema.load({"username": "valid", "email": "a@example.com", "password": "Str0ng@Pass"})
    assert data["username"] == "valid"


def test_register_schema_excludes_unknown_fields():
    schema = UserRegisterSchema()
    data = schema.load(
        {"username": "valid", "email": "a@example.com", "password": "Str0ng@Pass", "status": "admin"}
    )
    assert "status" not in data


def test_login_schema_requires_username_and_password():
    schema = LoginSchema()
    with pytest.raises(ValidationError):
        schema.load({"username": "valid"})


def test_note_create_schema_strips_whitespace_from_content_and_category():
    # Note: title itself can't reach the strip step with surrounding
    # whitespace — its Regexp validator (`^\S.*\S$`) rejects leading/trailing
    # whitespace during field deserialization, before @post_load runs. So
    # the strip_whitespace hook only ever has an effect on content/category.
    # See product_roadmap.md backlog for a note on tidying this up.
    schema = NoteCreateSchema()
    data = schema.load({"title": "Title", "content": "  Body  ", "category": "  Work  "})
    assert data["title"] == "Title"
    assert data["content"] == "Body"
    assert data["category"] == "Work"


def test_note_create_schema_rejects_leading_or_trailing_whitespace_in_title():
    schema = NoteCreateSchema()
    with pytest.raises(ValidationError):
        schema.load({"title": "  Title  ", "content": "Body"})


def test_note_create_schema_rejects_whitespace_only_title():
    schema = NoteCreateSchema()
    with pytest.raises(ValidationError):
        schema.load({"title": "   ", "content": "Body"})


def test_note_create_schema_rejects_title_over_20_chars():
    schema = NoteCreateSchema()
    with pytest.raises(ValidationError):
        schema.load({"title": "x" * 21, "content": "Body"})


def test_note_create_schema_ignores_unknown_fields():
    schema = NoteCreateSchema()
    data = schema.load({"title": "Ok", "content": "Body", "user_id": 99})
    assert "user_id" not in data


def test_note_update_schema_allows_partial_fields():
    schema = NoteUpdateSchema(partial=True)
    data = schema.load({"pinned": True})
    assert data == {"pinned": True}


def test_note_update_schema_rejects_category_over_30_chars():
    schema = NoteUpdateSchema()
    with pytest.raises(ValidationError):
        schema.load({"category": "x" * 31})


def test_password_change_schema_requires_both_fields():
    schema = PasswordChangeSchema()
    with pytest.raises(ValidationError):
        schema.load({"current_password": "Old@1234"})


def test_password_reset_schema_requires_strong_password():
    schema = PasswordResetSchema()
    with pytest.raises(ValidationError):
        schema.load({"token": "abc", "password": "weak"})


def test_self_update_schema_rejects_email_too_long():
    schema = SelfUpdateSchema()
    with pytest.raises(ValidationError):
        schema.load({"email": ("a" * 250) + "@example.com"})


def test_user_update_schema_rejects_invalid_status():
    schema = UserUpdateSchema()
    with pytest.raises(ValidationError):
        schema.load({"status": "superadmin"})


def test_user_update_schema_accepts_valid_status():
    schema = UserUpdateSchema()
    data = schema.load({"status": "admin"})
    assert data["status"] == "admin"
