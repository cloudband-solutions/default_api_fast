# Example Spec Stubs

```python
def test_index(client, auth_headers):
    response = client.get("/api/projects", headers=auth_headers)

    assert response.status_code == 200


def test_create(client, auth_headers):
    response = client.post(
        "/api/projects",
        headers=auth_headers,
        json={"name": "Project Atlas"},
    )

    assert response.status_code == 200
```
