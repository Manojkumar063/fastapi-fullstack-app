def test_signup_success(client):
    res = client.post("/api/v1/auth/signup", json={"email": "user@example.com", "password": "pass123"})
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "user@example.com"
    assert data["role"] == "user"
    assert data["is_active"] is True
    assert "id" in data

def test_signup_duplicate_email(client, registered_user):
    res = client.post("/api/v1/auth/signup", json=registered_user)
    assert res.status_code == 400
    assert res.json()["detail"] == "Email already registered"

def test_login_success(client, registered_user):
    res = client.post("/api/v1/auth/login", json=registered_user)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, registered_user):
    res = client.post("/api/v1/auth/login", json={"email": registered_user["email"], "password": "wrongpass"})
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid credentials"

def test_login_unknown_email(client):
    res = client.post("/api/v1/auth/login", json={"email": "nobody@example.com", "password": "pass"})
    assert res.status_code == 401

def test_me_authenticated(client, auth_headers):
    res = client.get("/api/v1/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@example.com"

def test_me_unauthenticated(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401

def test_me_invalid_token(client):
    res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalidtoken"})
    assert res.status_code == 401
