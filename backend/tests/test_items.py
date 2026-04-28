def test_create_item(client, auth_headers):
    res = client.post("/api/v1/items", json={"name": "Laptop", "description": "A laptop"}, headers=auth_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Laptop"
    assert data["description"] == "A laptop"
    assert "id" in data
    assert "owner_id" in data

def test_create_item_unauthenticated(client):
    res = client.post("/api/v1/items", json={"name": "Laptop"})
    assert res.status_code == 401

def test_list_items_empty(client, auth_headers):
    res = client.get("/api/v1/items", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []

def test_list_items(client, auth_headers):
    client.post("/api/v1/items", json={"name": "Item 1"}, headers=auth_headers)
    client.post("/api/v1/items", json={"name": "Item 2"}, headers=auth_headers)
    res = client.get("/api/v1/items", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2

def test_get_item(client, auth_headers):
    created = client.post("/api/v1/items", json={"name": "Phone"}, headers=auth_headers).json()
    res = client.get(f"/api/v1/items/{created['id']}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "Phone"

def test_get_item_not_found(client, auth_headers):
    res = client.get("/api/v1/items/999", headers=auth_headers)
    assert res.status_code == 404
    assert res.json()["detail"] == "Item not found"

def test_update_item(client, auth_headers):
    created = client.post("/api/v1/items", json={"name": "Old Name"}, headers=auth_headers).json()
    res = client.put(f"/api/v1/items/{created['id']}", json={"name": "New Name", "description": "Updated"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["name"] == "New Name"
    assert res.json()["description"] == "Updated"

def test_update_item_not_found(client, auth_headers):
    res = client.put("/api/v1/items/999", json={"name": "X"}, headers=auth_headers)
    assert res.status_code == 404

def test_delete_item(client, auth_headers):
    created = client.post("/api/v1/items", json={"name": "To Delete"}, headers=auth_headers).json()
    res = client.delete(f"/api/v1/items/{created['id']}", headers=auth_headers)
    assert res.status_code == 204

def test_delete_item_not_found(client, auth_headers):
    res = client.delete("/api/v1/items/999", headers=auth_headers)
    assert res.status_code == 404

def test_items_isolated_between_users(client):
    # User A creates an item
    client.post("/api/v1/auth/signup", json={"email": "a@example.com", "password": "pass123"})
    token_a = client.post("/api/v1/auth/login", json={"email": "a@example.com", "password": "pass123"}).json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    created = client.post("/api/v1/items", json={"name": "User A Item"}, headers=headers_a).json()

    # User B cannot see User A's item
    client.post("/api/v1/auth/signup", json={"email": "b@example.com", "password": "pass123"})
    token_b = client.post("/api/v1/auth/login", json={"email": "b@example.com", "password": "pass123"}).json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    res = client.get(f"/api/v1/items/{created['id']}", headers=headers_b)
    assert res.status_code == 404
