from models.audit_log import AuditLog
from main import app


def test_audit_log_requires_admin(client, auth_headers):
    response = client.get('/api/v1/admin/audit-log', headers=auth_headers)
    assert response.status_code == 403


def test_audit_log_requires_auth(client):
    response = client.get('/api/v1/admin/audit-log')
    assert response.status_code == 401


def test_creating_a_user_is_logged(client, admin_headers):
    client.post(
        '/api/v1/admin/users',
        json={"username": "logged", "email": "logged@example.com", "password": "Str0ng@Pass"},
        headers=admin_headers,
    )
    response = client.get('/api/v1/admin/audit-log', headers=admin_headers)
    assert response.status_code == 200
    entries = response.json['data']
    assert any(e['action'] == "user_created" and e['details'] == "logged" for e in entries)


def test_updating_a_user_is_logged(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    client.put(
        f'/api/v1/admin/users/{target_id}', json={"username": "renamed"}, headers=admin_headers
    )
    response = client.get('/api/v1/admin/audit-log', headers=admin_headers)
    entries = response.json['data']
    assert any(
        e['action'] == "user_updated" and e['target_id'] == target_id for e in entries
    )


def test_self_edit_by_non_admin_is_not_logged(client, auth_headers):
    me = client.get('/api/v1/me', headers=auth_headers).json
    client.put(
        f"/api/v1/admin/users/{me['id']}", json={"username": "selfrenamed"}, headers=auth_headers
    )
    with app.app_context():
        assert AuditLog.query.filter_by(action="user_updated").count() == 0


def test_deleting_a_user_is_logged(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    client.delete(f'/api/v1/admin/users/{target_id}', headers=admin_headers)
    response = client.get('/api/v1/admin/audit-log', headers=admin_headers)
    entries = response.json['data']
    assert any(
        e['action'] == "user_deleted" and e['target_id'] == target_id for e in entries
    )


def test_password_reset_issuance_is_logged(client, admin_headers, make_user):
    target_id = make_user(username="target", email="target@example.com")
    client.post(f'/api/v1/admin/users/{target_id}/reset-password', headers=admin_headers)
    response = client.get('/api/v1/admin/audit-log', headers=admin_headers)
    entries = response.json['data']
    assert any(
        e['action'] == "password_reset_issued" and e['target_id'] == target_id for e in entries
    )


def test_audit_log_is_paginated_newest_first(client, admin_headers, make_user):
    for i in range(3):
        make_user(username=f"aud{i}", email=f"aud{i}@example.com")
        client.post(
            '/api/v1/admin/users',
            json={"username": f"created{i}", "email": f"created{i}@example.com", "password": "Str0ng@Pass"},
            headers=admin_headers,
        )
    response = client.get('/api/v1/admin/audit-log?page=1&per_page=2', headers=admin_headers)
    assert response.status_code == 200
    assert len(response.json['data']) == 2
    assert response.json['pagination']['per_page'] == 2
    timestamps = [e['created_at'] for e in response.json['data']]
    assert timestamps == sorted(timestamps, reverse=True)
