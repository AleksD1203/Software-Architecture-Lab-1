import pytest
from fastapi.testclient import TestClient
from main import app, users_db, recipes_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    users_db.clear()
    recipes_db.clear()
    yield

@pytest.fixture
def auth_headers():
    user_data = {"email": "student@kpi.ua", "password": "password123"}
    client.post("/register", json=user_data)
    login_res = client.post("/login", json=user_data)
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 1. Тест реєстрації та конфлікту
def test_register_and_conflict():
    user_data = {"email": "test_user@kpi.ua", "password": "password123"}
    # Перша реєстрація
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    
    # Повторна реєстрація (має бути 409)
    response_conflict = client.post("/register", json=user_data)
    assert response_conflict.status_code == 409

# 2. Тест інваріантів: валідація пароля
def test_register_invalid_password():
    response = client.post("/register", json={
        "email": "bad@kpi.ua",
        "password": "123"  # Занадто короткий
    })
    assert response.status_code == 422

# 3. Тест авторизації та отримання токена
def test_login_success():
    client.post("/register", json={"email": "login@kpi.ua", "password": "password123"})
    response = client.post("/login", json={"email": "login@kpi.ua", "password": "password123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

# 4. Тест створення рецепта
def test_create_recipe(auth_headers):
    recipe_data = {
        "title": "Борщ",
        "cooking_time": 120,
        "ingredients": ["Буряк", "М'ясо", "Капуста"]
    }
    
    response = client.post("/recipes", json=recipe_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Борщ"

# 5. Тест інваріантів: час приготування
def test_create_recipe_invalid_time(auth_headers):
    response = client.post("/recipes", json={
        "title": "Хвилинка",
        "cooking_time": 0,
        "ingredients": ["вода"]
    }, headers=auth_headers)
    assert response.status_code == 422

# 6. Тест захисту: доступ без токена
def test_unauthorized_recipe_creation():
    response = client.post("/recipes", json={
        "title": "Secret",
        "cooking_time": 10,
        "ingredients": []
    })
    assert response.status_code == 401

# 7. Отримання списку рецептів
def test_get_recipes(auth_headers):
    client.post("/recipes", json={
        "title": "Десерт",
        "cooking_time": 30,
        "ingredients": ["Яблука", "Кориця", "Цукор"]
    }, headers=auth_headers)
    
    response = client.get("/recipes")
    assert response.status_code == 200
    assert len(response.json()) == 1

# 8. Видалення свого рецепта
def test_delete_own_recipe(auth_headers):
    create_res = client.post("/recipes", json={
        "title": "Рецепт на видалення",
        "cooking_time": 15,
        "ingredients": ["сіль"]
    }, headers=auth_headers)
    
    recipe_id = create_res.json()["id"]
    
    del_res = client.delete(f"/recipes/{recipe_id}", headers=auth_headers)
    assert del_res.status_code == 204
    
    get_res = client.get("/recipes")
    assert len(get_res.json()) == 0

# 9. Спроба видалити чужий рецепт
def test_delete_others_recipe(auth_headers):
    create_res = client.post("/recipes", json={
        "title": "Чужий рецепт",
        "cooking_time": 60,
        "ingredients": ["секретний інгредієнт"]
    }, headers=auth_headers)
    recipe_id = create_res.json()["id"]
    
    user2 = {"email": "hacker@kpi.ua", "password": "password123"}
    client.post("/register", json=user2)
    token2 = client.post("/login", json=user2).json()["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}
    
    del_res = client.delete(f"/recipes/{recipe_id}", headers=headers2)
    assert del_res.status_code == 403
