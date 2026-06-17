import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_create_question(client: AsyncClient, admin_token_headers: dict):
    payload = {
        "text": "Какой паттерн проектирования гарантирует наличие единственного экземпляра класса?",
        "option_a": "Factory Method",
        "option_b": "Singleton",
        "option_c": "Observer",
        "option_d": "Decorator",
        "correct_option": "option_b"
    }
    
    response = await client.post("/questions/", json=payload, headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == payload["text"]
    assert data["correct_option"] == payload["correct_option"]
    assert "id" in data

async def test_get_questions(client: AsyncClient, admin_token_headers: dict):
    response = await client.get("/questions/", headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

async def test_update_question(client: AsyncClient, admin_token_headers: dict):
    create_payload = {
        "text": "Временный вопрос",
        "option_a": "1",
        "option_b": "2",
        "option_c": "3",
        "option_d": "4",
        "correct_option": "option_a"
    }
    create_resp = await client.post("/questions/", json=create_payload, headers=admin_token_headers)
    question_id = create_resp.json()["id"]

    update_payload = {
        "text": "Обновленный вопрос",
        "correct_option": "option_c"
    }
    response = await client.put(f"/questions/{question_id}", json=update_payload, headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Обновленный вопрос"
    assert data["correct_option"] == "option_c"

async def test_delete_question(client: AsyncClient, admin_token_headers: dict):
    create_payload = {
        "text": "Вопрос для удаления",
        "option_a": "1",
        "option_b": "2",
        "option_c": "3",
        "option_d": "4",
        "correct_option": "option_a"
    }
    create_resp = await client.post("/questions/", json=create_payload, headers=admin_token_headers)
    question_id = create_resp.json()["id"]

    response = await client.delete(f"/questions/{question_id}", headers=admin_token_headers)
    
    assert response.status_code == 200
    assert response.json() == {"msg": "Question deleted"}

async def test_question_not_found(client: AsyncClient, admin_token_headers: dict):
    non_existent_id = 999999
    
    put_response = await client.put(
        f"/questions/{non_existent_id}", 
        json={"text": "Новый текст"}, 
        headers=admin_token_headers
    )
    assert put_response.status_code == 404
    assert put_response.json() == {"detail": "Question not found"}

    delete_response = await client.delete(
        f"/questions/{non_existent_id}", 
        headers=admin_token_headers
    )
    assert delete_response.status_code == 404
    assert delete_response.json() == {"detail": "Question not found"}