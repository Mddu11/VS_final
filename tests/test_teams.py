import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_team(client: AsyncClient, admin_token_headers: dict):
    payload = {
        "name": "Dream Team"
    }
    
    response = await client.post("/teams/", json=payload, headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == payload["name"]
    assert "id" in data

async def test_get_teams(client: AsyncClient):
    response = await client.get("/teams/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

async def test_update_team(client: AsyncClient, admin_token_headers: dict):
    create_payload = {"name": "Old Team Name"}
    create_resp = await client.post("/teams/", json=create_payload, headers=admin_token_headers)
    team_id = create_resp.json()["id"]

    update_payload = {"name": "New Team Name"}
    response = await client.put(f"/teams/{team_id}", json=update_payload, headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_payload["name"]

async def test_delete_team(client: AsyncClient, admin_token_headers: dict):
    create_payload = {"name": "Team to delete"}
    create_resp = await client.post("/teams/", json=create_payload, headers=admin_token_headers)
    team_id = create_resp.json()["id"]

    response = await client.delete(f"/teams/{team_id}", headers=admin_token_headers)
    
    assert response.status_code == 200
    assert response.json() == {"msg": "Team deleted"}

async def test_team_not_found(client: AsyncClient, admin_token_headers: dict):
    non_existent_id = 999999
    
    put_response = await client.put(
        f"/teams/{non_existent_id}", 
        json={"name": "Ghost Team"}, 
        headers=admin_token_headers
    )
    assert put_response.status_code == 404
    assert put_response.json() == {"detail": "Team not found"}

    delete_response = await client.delete(
        f"/teams/{non_existent_id}", 
        headers=admin_token_headers
    )
    assert delete_response.status_code == 404
    assert delete_response.json() == {"detail": "Team not found"}