def test_create_user(client):
    with client as c:
        response = c.post(
            "/user",
            json={
                "name": "username",
                "email_address": "user@example.com",
                "plaintext_password": "pasword",
            },
        )
    assert response.status_code == 201
    assert response.json() == {
        "name": "username",
        "email_address": "user@example.com",
        "user_id": 1,
    }


def test_create_user_duplicate(create_user, client):
    with client as c:
        response = c.post(
            "/user",
            json={
                "name": "username",
                "email_address": "user@example.com",
                "plaintext_password": "pasword",
            },
        )
    assert response.status_code == 409
    assert response.json() == {"detail": "User already registered"}


def test_options_create_user(client):
    response = client.options("/user")
    assert response.status_code == 200
    assert response.headers == {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "OPTIONS, POST",
        "access-control-allow-headers": "accept, Content-Type, Authorization",
        "content-length": "0",
    }


def test_login(create_user, client):
    with client as c:
        response = c.post(
            "/token",
            data={
                "grant_type": "password",
                "username": "username",
                "password": "password",
            },
        )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(create_user, client):
    with client as c:
        response = c.post(
            "/token",
            data={
                "grant_type": "password",
                "username": "username",
                "password": "invalid_password",
            },
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_login_nonexistent(client):
    with client as c:
        response = c.post(
            "/token",
            data={
                "grant_type": "password",
                "username": "username",
                "password": "password",
            },
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect username or password"}


def test_read_users_me(create_token, client):
    with client as c:
        response = c.get(
            "/user/me", headers={"Authorization": f"Bearer {create_token}"}
        )

    assert response.status_code == 200
    assert response.json() == {
        "name": "username",
        "email_address": "user@example.com",
        "user_id": 1,
    }


def test_read_users_me_no_token(client):
    with client as c:
        response = c.get("/user/me")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_read_users_me_invalid_token(client):
    with client as c:
        response = c.get("/user/me", headers={"Authorization": "Bearer invalid_token"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_options_read_users_me(client):
    response = client.options("/user/me")
    assert response.status_code == 200
    assert response.headers == {
        "access-control-allow-origin": "*",
        "access-control-allow-methods": "GET, OPTIONS",
        "access-control-allow-headers": "accept, Authorization",
        "content-length": "0",
    }
