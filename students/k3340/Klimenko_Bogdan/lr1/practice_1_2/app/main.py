from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, select, Session
from .db import get_session, init_db
from .models import (
    Warrior, WarriorDefault, WarriorWithRelations,
    Profession, Skill, SkillWarriorLink
)
from typing import Optional, List

app = FastAPI(title="Warriors API with SQLModel")

@app.on_event("startup")
def on_startup():
    init_db()

# ---------- Warriors ----------
@app.get("/warriors", response_model=list[WarriorWithRelations])
def get_warriors(session: Session = Depends(get_session)):
    warriors = session.exec(select(Warrior)).all()
    return warriors

@app.get("/warriors/{warrior_id}", response_model=WarriorWithRelations)
def get_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior

@app.post("/warriors", response_model=WarriorWithRelations, status_code=201)
def create_warrior(warrior: WarriorDefault, session: Session = Depends(get_session)):
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@app.patch("/warriors/{warrior_id}", response_model=WarriorWithRelations)
def update_warrior(warrior_id: int, warrior_update: WarriorDefault, session: Session = Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    update_data = warrior_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_warrior, key, value)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@app.delete("/warriors/{warrior_id}")
def delete_warrior(warrior_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"ok": True}

# ---------- Professions ----------
class ProfessionDefault(SQLModel):
    title: str
    description: str

@app.get("/professions", response_model=list[Profession])
def get_professions(session: Session = Depends(get_session)):
    return session.exec(select(Profession)).all()

@app.get("/professions/{profession_id}", response_model=Profession)
def get_profession(profession_id: int, session: Session = Depends(get_session)):
    prof = session.get(Profession, profession_id)
    if not prof:
        raise HTTPException(status_code=404, detail="Profession not found")
    return prof

@app.post("/professions", response_model=Profession, status_code=201)
def create_profession(prof: ProfessionDefault, session: Session = Depends(get_session)):
    db_prof = Profession.model_validate(prof)
    session.add(db_prof)
    session.commit()
    session.refresh(db_prof)
    return db_prof

# ---------- Skills (many-to-many) ----------
class SkillDefault(SQLModel):
    name: str
    description: Optional[str] = ""

@app.get("/skills", response_model=list[Skill])
def get_skills(session: Session = Depends(get_session)):
    return session.exec(select(Skill)).all()

@app.post("/skills", response_model=Skill, status_code=201)
def create_skill(skill: SkillDefault, session: Session = Depends(get_session)):
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill

@app.post("/warriors/{warrior_id}/skills/{skill_id}")
def add_skill_to_warrior(warrior_id: int, skill_id: int, session: Session = Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)
    if not warrior or not skill:
        raise HTTPException(status_code=404, detail="Warrior or Skill not found")
    if skill not in warrior.skills:
        warrior.skills.append(skill)
        session.commit()
    return {"ok": True}