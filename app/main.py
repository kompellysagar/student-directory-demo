from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import inspect

from app.api.chat import router as chat_router
from app.api.students import router as students_router
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import Student

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Seed only a brand-new database, so deleting all records stays intentional.
    seed_demo_data = not inspect(engine).has_table(Student.__tablename__)
    Base.metadata.create_all(bind=engine)
    if seed_demo_data:
        with SessionLocal() as db:
            db.add_all(
                [
                    Student(
                        name="Asha Kumar",
                        email="asha@example.com",
                        course="Computer Science",
                        year=3,
                    ),
                    Student(
                        name="Rohan Patel",
                        email="rohan@example.com",
                        course="Business Administration",
                        year=2,
                    ),
                    Student(
                        name="Maya Singh",
                        email="maya@example.com",
                        course="Information Technology",
                        year=4,
                    ),
                ]
            )
            db.commit()
    yield

app = FastAPI(
    title=settings.app_name,
    description="A student directory with CRUD endpoints and an optional Gemini chatbot.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(students_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root():
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "service": settings.app_name}
