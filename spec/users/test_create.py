def test_create_user_defaults_role_to_user(client, auth_headers):
    response = client.post(
        "/users",
        headers=auth_headers,
        json={
            "email": "new-user@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password",
            "password_confirmation": "password",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "new-user@example.com"
    assert response.json()["role"] == "user"


def test_create_user_with_admin_role(client, auth_headers):
    response = client.post(
        "/users",
        headers=auth_headers,
        json={
            "email": "admin-user@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "password": "password",
            "password_confirmation": "password",
        },
    )

    assert response.status_code == 201
    assert response.json()["role"] == "admin"


def test_create_user_rejects_invalid_role(client, auth_headers):
    response = client.post(
        "/users",
        headers=auth_headers,
        json={
            "email": "invalid-role@example.com",
            "first_name": "Invalid",
            "last_name": "Role",
            "role": "superadmin",
            "password": "password",
            "password_confirmation": "password",
        },
    )

    assert response.status_code == 422
    assert response.json()["role"] == ["invalid"]
