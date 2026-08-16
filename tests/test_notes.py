def create_note(client, headers, **overrides):
    payload = {"title": "Groceries", "content": "Milk, eggs"}
    payload.update(overrides)
    return client.post('/api/v1/notes', json=payload, headers=headers)


def test_create_note(client, auth_headers):
    response = create_note(client, auth_headers)
    assert response.status_code == 201
    assert response.json['message'] == "Note created"
    assert "note_id" in response.json['data']


def test_create_note_invalid_title(client, auth_headers):
    response = create_note(client, auth_headers, title="   ")
    assert response.status_code == 400
    assert response.json['message'] == "Validation error"


def test_create_note_title_too_long(client, auth_headers):
    response = create_note(client, auth_headers, title="x" * 21)
    assert response.status_code == 400


def test_create_note_requires_auth(client, csrf_token):
    response = client.post(
        '/api/v1/notes',
        json={"title": "x", "content": "y"},
        headers={"X-CSRF-Token": csrf_token},
    )
    assert response.status_code == 401


def test_create_note_requires_csrf(client, auth_headers):
    headers = {"Authorization": auth_headers["Authorization"]}
    response = create_note(client, headers)
    assert response.status_code == 400


def test_create_note_duplicate_title_for_same_user(client, auth_headers):
    create_note(client, auth_headers, title="Dup")
    response = create_note(client, auth_headers, title="Dup")
    assert response.status_code == 400


def test_create_note_same_title_different_user_ok(client, auth_headers, admin_headers):
    r1 = create_note(client, auth_headers, title="Shared")
    r2 = create_note(client, admin_headers, title="Shared")
    assert r1.status_code == 201
    assert r2.status_code == 201


def test_create_note_with_category(client, auth_headers):
    response = create_note(client, auth_headers, category="Work")
    assert response.status_code == 201


def test_create_note_content_too_long(client, auth_headers):
    response = create_note(client, auth_headers, content="x" * 20001)
    assert response.status_code == 400


def test_create_note_category_too_long(client, auth_headers):
    response = create_note(client, auth_headers, category="x" * 31)
    assert response.status_code == 400


def test_list_notes_excludes_trashed(client, auth_headers):
    create_note(client, auth_headers, title="Active")
    trashed = create_note(client, auth_headers, title="Trashed").json['data']['note_id']
    client.delete(f'/api/v1/notes/{trashed}', headers=auth_headers)

    response = client.get('/api/v1/notes', headers=auth_headers)
    assert response.status_code == 200
    titles = [n['title'] for n in response.json['data']]
    assert titles == ["Active"]


def test_list_notes_requires_auth(client):
    response = client.get('/api/v1/notes')
    assert response.status_code == 401


def test_list_notes_is_paginated(client, auth_headers):
    for i in range(3):
        create_note(client, auth_headers, title=f"Note {i}")

    response = client.get('/api/v1/notes?page=1&per_page=2', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json['data']) == 2
    assert response.json['pagination'] == {
        "page": 1, "per_page": 2, "total": 3, "total_pages": 2
    }

    response = client.get('/api/v1/notes?page=2&per_page=2', headers=auth_headers)
    assert len(response.json['data']) == 1
    assert response.json['pagination']['page'] == 2


def test_list_notes_pinned_first(client, auth_headers):
    create_note(client, auth_headers, title="Unpinned")
    pinned_id = create_note(client, auth_headers, title="Pinned").json['data']['note_id']
    client.patch(f'/api/v1/notes/{pinned_id}', json={"pinned": True}, headers=auth_headers)

    response = client.get('/api/v1/notes', headers=auth_headers)
    assert response.json['data'][0]['id'] == pinned_id


def test_get_note(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.get(f'/api/v1/notes/{note_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['title'] == "Groceries"


def test_get_note_not_found(client, auth_headers):
    response = client.get('/api/v1/notes/9999', headers=auth_headers)
    assert response.status_code == 404


def test_get_note_forbidden_for_other_user(client, auth_headers, admin_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.get(f'/api/v1/notes/{note_id}', headers=admin_headers)
    assert response.status_code == 403


def test_get_trashed_note_returns_404(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = client.get(f'/api/v1/notes/{note_id}', headers=auth_headers)
    assert response.status_code == 404


def test_patch_note_title(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.patch(
        f'/api/v1/notes/{note_id}', json={"title": "Renamed"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json['data']['title'] == "Renamed"


def test_patch_note_pinned(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.patch(
        f'/api/v1/notes/{note_id}', json={"pinned": True}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json['data']['pinned'] is True


def test_patch_note_category(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.patch(
        f'/api/v1/notes/{note_id}', json={"category": "Personal"}, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json['data']['category'] == "Personal"


def test_patch_note_invalid_title(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.patch(
        f'/api/v1/notes/{note_id}', json={"title": "   "}, headers=auth_headers
    )
    assert response.status_code == 400


def test_patch_note_forbidden_for_other_user(client, auth_headers, admin_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.patch(
        f'/api/v1/notes/{note_id}', json={"title": "Hijacked"}, headers=admin_headers
    )
    assert response.status_code == 403


def test_patch_trashed_note_returns_404(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = client.patch(
        f'/api/v1/notes/{note_id}', json={"title": "Nope"}, headers=auth_headers
    )
    assert response.status_code == 404


def test_delete_note_moves_to_trash(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == "Note moved to trash"


def test_delete_note_forbidden_for_other_user(client, auth_headers, admin_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.delete(f'/api/v1/notes/{note_id}', headers=admin_headers)
    assert response.status_code == 403


def test_delete_already_trashed_note_returns_404(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    assert response.status_code == 404


def test_trashing_note_frees_title_for_reuse(client, auth_headers):
    note_id = create_note(client, auth_headers, title="Reuse").json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = create_note(client, auth_headers, title="Reuse")
    assert response.status_code == 201


def test_list_trash(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = client.get('/api/v1/notes/trash', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['id'] == note_id
    assert response.json['pagination']['total'] == 1


def test_list_trash_excludes_active(client, auth_headers):
    create_note(client, auth_headers)
    response = client.get('/api/v1/notes/trash', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['data'] == []


def test_restore_note(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = client.post(f'/api/v1/notes/{note_id}/restore', headers=auth_headers)
    assert response.status_code == 200

    get_response = client.get(f'/api/v1/notes/{note_id}', headers=auth_headers)
    assert get_response.status_code == 200


def test_restore_note_not_trashed_returns_404(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.post(f'/api/v1/notes/{note_id}/restore', headers=auth_headers)
    assert response.status_code == 404


def test_restore_note_forbidden_for_other_user(client, auth_headers, admin_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = client.post(f'/api/v1/notes/{note_id}/restore', headers=admin_headers)
    assert response.status_code == 403


def test_restore_note_title_conflict(client, auth_headers):
    note_id = create_note(client, auth_headers, title="Conflict").json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    create_note(client, auth_headers, title="Conflict")
    response = client.post(f'/api/v1/notes/{note_id}/restore', headers=auth_headers)
    assert response.status_code == 400


def test_permanent_delete(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = client.delete(f'/api/v1/notes/{note_id}/permanent', headers=auth_headers)
    assert response.status_code == 200

    trash_response = client.get('/api/v1/notes/trash', headers=auth_headers)
    assert trash_response.json['data'] == []


def test_permanent_delete_requires_trashed_first(client, auth_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    response = client.delete(f'/api/v1/notes/{note_id}/permanent', headers=auth_headers)
    assert response.status_code == 404


def test_permanent_delete_forbidden_for_other_user(client, auth_headers, admin_headers):
    note_id = create_note(client, auth_headers).json['data']['note_id']
    client.delete(f'/api/v1/notes/{note_id}', headers=auth_headers)
    response = client.delete(f'/api/v1/notes/{note_id}/permanent', headers=admin_headers)
    assert response.status_code == 403
