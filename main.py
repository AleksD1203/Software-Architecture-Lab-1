from fastapi import FastAPI, HTTPException, Depends
from schemas import UserSchema, RecipeSchema
from auth import create_token, get_current_user

app = FastAPI(title="Кулінарна книга - Структурована")

users_db = {}
recipes_db = {}
id_counter = 1

@app.post("/register", status_code=201)
def register(user: UserSchema):
    if user.email in users_db:
        raise HTTPException(status_code=409, detail="User exists")
    users_db[user.email] = user.password
    return {"status": "ok"}

@app.post("/login")
def login(user: UserSchema):
    if user.email not in users_db or users_db[user.email] != user.password:
        raise HTTPException(status_code=401, detail="Wrong credentials")
    return {"access_token": create_token(user.email)}

@app.get("/recipes")
def list_recipes():
    return list(recipes_db.values())

@app.post("/recipes", status_code=201)
def create_recipe(recipe: RecipeSchema, user: str = Depends(get_current_user)):
    global id_counter
    data = recipe.model_dump()
    data["id"] = id_counter
    data["author"] = user
    recipes_db[id_counter] = data
    id_counter += 1
    return data

@app.delete("/recipes/{r_id}", status_code=204)
def delete_recipe(r_id: int, user: str = Depends(get_current_user)):
    if r_id not in recipes_db:
        raise HTTPException(status_code=404, detail="Not found")
    if recipes_db[r_id]["author"] != user:
        raise HTTPException(status_code=403, detail="Not yours")
    del recipes_db[r_id]
    return