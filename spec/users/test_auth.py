def test_users_requires_authentication(client):
    response = client.get("/users")

    assert response.status_code == 401


def test_users_crud_requires_admin_role(client, user_auth_headers, db_session):
    from spec.factories import UserFactory

    user = UserFactory()

    responses = [
        client.get("/users", headers=user_auth_headers),
        client.get(f"/users/{user.id}", headers=user_auth_headers),
        client.post(
            "/users",
            headers=user_auth_headers,
            json={
                "email": "member@example.com",
                "first_name": "Member",
                "last_name": "User",
                "password": "password",
                "password_confirmation": "password",
            },
        ),
        client.put(
            f"/users/{user.id}",
            headers=user_auth_headers,
            json={"first_name": "Updated"},
        ),
        client.delete(f"/users/{user.id}", headers=user_auth_headers),
    ]

    for response in responses:
        assert response.status_code == 403
        assert response.json()["detail"] == "unauthorized"
