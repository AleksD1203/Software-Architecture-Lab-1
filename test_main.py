from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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
def test_create_recipe():
    login_res = client.post("/login", json={"email": "login@kpi.ua", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    recipe_data = {
        "title": "Борщ",
        "cooking_time": 120,
        "ingredients": ["Буряк", "М'ясо", "Капуста"]
    }
    
    response = client.post("/recipes", json=recipe_data, headers=headers)
    assert response.status_code == 201
    assert response.json()["title"] == "Борщ"

# 5. Тест інваріантів: час приготування
def test_create_recipe_invalid_time():
    login_res = client.post("/login", json={"email": "login@kpi.ua", "password": "password123"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = client.post("/recipes", json={
        "title": "Хвилинка",
        "cooking_time": 0,  # Має бути > 0
        "ingredients": ["вода"]
    }, headers=headers)
    assert response.status_code == 422

# 6. Тест захисту: доступ без токена
def test_unauthorized_recipe_creation():
    response = client.post("/recipes", json={
        "title": "Secret",
        "cooking_time": 10,
        "ingredients": []
    })
    assert response.status_code == 401