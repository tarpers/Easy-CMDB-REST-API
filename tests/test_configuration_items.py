from fastapi.testclient import TestClient

URL = "/configuration-items/"


def create_ci(client: TestClient, **overrides: object) -> dict:
    payload = {"name": "web-01", "ci_type": "server"} | overrides
    response = client.post(URL, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_create_configuration_item(client: TestClient) -> None:
    data = create_ci(client, owner="ops", description="Frontend web server")
    assert data["id"] >= 1
    assert data["name"] == "web-01"
    assert data["ci_type"] == "server"
    assert data["status"] == "planned"
    assert data["owner"] == "ops"
    assert "created_at" in data and "updated_at" in data


def test_create_rejects_invalid_payload(client: TestClient) -> None:
    response = client.post(URL, json={"name": "", "ci_type": "spaceship"})
    assert response.status_code == 422


def test_read_configuration_item(client: TestClient) -> None:
    created = create_ci(client)
    response = client.get(f"{URL}{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_read_missing_returns_404(client: TestClient) -> None:
    response = client.get(f"{URL}999")
    assert response.status_code == 404


def test_list_with_filters_and_pagination(client: TestClient) -> None:
    create_ci(client, name="web-01", ci_type="server", status="active")
    create_ci(client, name="db-01", ci_type="database", status="active")
    create_ci(client, name="web-02", ci_type="server", status="retired")

    assert len(client.get(URL).json()) == 3

    servers = client.get(URL, params={"ci_type": "server"}).json()
    assert {ci["name"] for ci in servers} == {"web-01", "web-02"}

    active_servers = client.get(URL, params={"ci_type": "server", "status": "active"})
    assert [ci["name"] for ci in active_servers.json()] == ["web-01"]

    page = client.get(URL, params={"offset": 1, "limit": 1}).json()
    assert [ci["name"] for ci in page] == ["db-01"]


def test_update_configuration_item(client: TestClient) -> None:
    created = create_ci(client)
    response = client.patch(f"{URL}{created['id']}", json={"status": "active"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["name"] == created["name"]
    assert data["updated_at"] >= created["updated_at"]


def test_delete_configuration_item(client: TestClient) -> None:
    created = create_ci(client)
    response = client.delete(f"{URL}{created['id']}")
    assert response.status_code == 204
    assert client.get(f"{URL}{created['id']}").status_code == 404
