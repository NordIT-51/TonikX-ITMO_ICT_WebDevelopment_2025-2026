from .celery_app import celery_app
from .parser import parse_url_async
from .database import SessionLocal
from .models import ParsedPage
import asyncio
from datetime import datetime, timedelta

@celery_app.task
def parse_url_task(url: str):
    """
    Задача для асинхронного парсинга URL.
    Запускается в Celery-воркере.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(parse_url_async(url))
    finally:
        loop.close()

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
    except Exception as e:
        db.rollback()
        result = {"url": url, "status": "error", "error": str(e)}
    finally:
        db.close()

    return result

@celery_app.task
def cleanup_old_pages():
    """
    Периодическая задача: удаляет записи старше 7 дней.
    """
    db = SessionLocal()
    cutoff = datetime.utcnow() - timedelta(days=7)
    try:
        deleted = db.query(ParsedPage).filter(ParsedPage.created_at < cutoff).delete()
        db.commit()
        return {"deleted": deleted}
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()