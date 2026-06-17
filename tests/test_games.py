import pytest
from httpx import AsyncClient

# Применяем маркер asyncio ко всем тестам в этом файле
pytestmark = pytest.mark.asyncio

async def test_create_game(client: AsyncClient, admin_token_headers: dict):
    payload = {
        "scheduled_time": "2026-06-01T15:00:00"
    }
    
    response = await client.post("/games/", json=payload, headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["scheduled_time"] == payload["scheduled_time"]
    assert "id" in data

async def test_update_game(client: AsyncClient, admin_token_headers: dict):
    create_payload = {"scheduled_time": "2026-06-02T15:00:00"}
    create_resp = await client.post("/games/", json=create_payload, headers=admin_token_headers)
    game_id = create_resp.json()["id"]

    update_payload = {"is_active": True}
    response = await client.put(f"/games/{game_id}", json=update_payload, headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True

async def test_delete_game(client: AsyncClient, admin_token_headers: dict):
    create_payload = {"scheduled_time": "2026-06-03T15:00:00"}
    create_resp = await client.post("/games/", json=create_payload, headers=admin_token_headers)
    game_id = create_resp.json()["id"]

    response = await client.delete(f"/games/{game_id}", headers=admin_token_headers)
    
    assert response.status_code == 200
    assert response.json() == {"msg": "Game deleted"}

async def test_game_not_found(client: AsyncClient, admin_token_headers: dict):
    non_existent_id = 999999
    
    put_response = await client.put(
        f"/games/{non_existent_id}", 
        json={"is_active": True}, 
        headers=admin_token_headers
    )
    assert put_response.status_code == 404
    assert put_response.json() == {"detail": "Game not found"}

    delete_response = await client.delete(
        f"/games/{non_existent_id}", 
        headers=admin_token_headers
    )
    assert delete_response.status_code == 404
    assert delete_response.json() == {"detail": "Game not found"}