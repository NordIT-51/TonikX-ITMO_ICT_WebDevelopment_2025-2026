from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

app = FastAPI(title="Practice 1.1 - Warriors API")

# ========== Временная база данных ==========
temp_bd = [
    {
        "id": 1,
        "race": "director",
        "name": "Мартынов Дмитрий",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Влиятельный человек",
            "description": "Эксперт по всем вопросам"
        },
        "skills": [
            {
                "id": 1,
                "name": "Купле-продажа компрессоров",
                "description": ""
            },
            {
                "id": 2,
                "name": "Оценка имущества",
                "description": ""
            }
        ]
    },
    {
        "id": 2,
        "race": "worker",
        "name": "Андрей Косякин",
        "level": 12,
        "profession": {
            "id": 1,
            "title": "Дельфист-гребец",
            "description": "Уважаемый сотрудник"
        },
        "skills": []
    }
]

# ========== Pydantic модели ==========
class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"

class Profession(BaseModel):
    id: int
    title: str
    description: str

class Skill(BaseModel):
    id: int
    name: str
    description: str

class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []

# ========== Эндпоинты для воинов ==========
@app.get("/warriors", response_model=List[Warrior])
def get_warriors():
    """Получить список всех воинов"""
    return temp_bd

@app.get("/warriors/{warrior_id}", response_model=Warrior)
def get_warrior(warrior_id: int):
    """Получить одного воина по id"""
    for warrior in temp_bd:
        if warrior["id"] == warrior_id:
            return warrior
    raise HTTPException(status_code=404, detail="Warrior not found")

@app.post("/warriors", status_code=201)
def create_warrior(warrior: Warrior):
    """Создать нового воина"""
    # Проверяем уникальность id
    for w in temp_bd:
        if w["id"] == warrior.id:
            raise HTTPException(status_code=400, detail="Warrior with this id already exists")
    temp_bd.append(warrior.model_dump())
    return {"status": "created", "data": warrior}

@app.put("/warriors/{warrior_id}")
def update_warrior(warrior_id: int, warrior: Warrior):
    """Полностью обновить воина"""
    for i, w in enumerate(temp_bd):
        if w["id"] == warrior_id:
            # Проверяем, что id в теле совпадает с id в пути (опционально)
            if warrior.id != warrior_id:
                raise HTTPException(status_code=400, detail="ID in path and body do not match")
            temp_bd[i] = warrior.model_dump()
            return {"status": "updated", "data": warrior}
    raise HTTPException(status_code=404, detail="Warrior not found")

@app.delete("/warriors/{warrior_id}")
def delete_warrior(warrior_id: int):
    """Удалить воина"""
    for i, w in enumerate(temp_bd):
        if w["id"] == warrior_id:
            temp_bd.pop(i)
            return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Warrior not found")

# ========== Дополнительно: API для профессий (вложенный объект) ==========
# Профессии хранятся внутри воинов, но для демонстрации сделаем отдельный список
professions_bd = [
    {"id": 1, "title": "Влиятельный человек", "description": "Эксперт по всем вопросам"},
    {"id": 2, "title": "Дельфист-гребец", "description": "Уважаемый сотрудник"}
]

@app.get("/professions", response_model=List[Profession])
def get_professions():
    return professions_bd

@app.post("/professions", status_code=201)
def create_profession(profession: Profession):
    for p in professions_bd:
        if p["id"] == profession.id:
            raise HTTPException(status_code=400, detail="Profession already exists")
    professions_bd.append(profession.model_dump())
    return {"status": "created", "data": profession}