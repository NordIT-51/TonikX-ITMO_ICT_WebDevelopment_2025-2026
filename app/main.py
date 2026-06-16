from fastapi import FastAPI
from .routers import users, trips, applications, messages, reviews
from .database import engine, Base

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