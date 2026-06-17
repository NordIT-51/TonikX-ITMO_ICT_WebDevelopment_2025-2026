from fastapi import FastAPI, HTTPException, Depends
from .routers import users, trips, applications, messages, reviews
from .database import engine, Base, SessionLocal
from .models import User, ParsedPage          # Добавим ParsedPage
from .auth import get_current_active_user
from .parser import parse_url_async
from .tasks import parse_url_task
from .celery_app import celery_app

# Раскомментируйте следующую строку, если хотите создавать таблицы автоматически (без Alembic)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="Travel Companion API", version="1.0")

app.include_router(users.router)
app.include_router(trips.router)
app.include_router(applications.router)
app.include_router(messages.router)
app.include_router(reviews.router)

@app.get("/")
def root():
    return {"message": "Travel Companion API is running"}

# ========== НОВЫЕ ЭНДПОИНТЫ ДЛЯ ПАРСИНГА ==========

@app.post("/parse-sync")
async def parse_sync(url: str, current_user: User = Depends(get_current_active_user)):
    """
    Синхронный вызов парсера – ждёт завершения и возвращает результат.
    Полезно для коротких запросов.
    """
    try:
        result = await parse_url_async(url)
        # Сохраняем результат в БД
        db = SessionLocal()
        try:
            page = ParsedPage(
                url=result.get("url"),
                title=result.get("title"),
                content=result.get("content")
            )
            db.add(page)
            db.commit()
            db.refresh(page)
            result["id"] = page.id
            result["status"] = "success"
            return {"status": "ok", "result": result}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"DB error: {str(e)}")
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse-async")
def parse_async(url: str, current_user: User = Depends(get_current_active_user)):
    """
    Асинхронный вызов через Celery – сразу возвращает task_id.
    Результат можно получить позже через /task-status.
    """
    task = parse_url_task.delay(url)
    return {"task_id": task.id, "status": "queued"}

@app.get("/task-status/{task_id}")
def get_task_status(task_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Проверка статуса задачи Celery.
    """
    task = celery_app.AsyncResult(task_id)
    if task.ready():
        return {"status": "completed", "result": task.result}
    else:
        return {"status": "pending"}

@app.get("/pages")
def get_pages(skip: int = 0, limit: int = 10, current_user: User = Depends(get_current_active_user)):
    """
    Список сохранённых страниц (результатов парсинга) с пагинацией.
    """
    db = SessionLocal()
    try:
        pages = db.query(ParsedPage).offset(skip).limit(limit).all()
        return pages
    finally:
        db.close()