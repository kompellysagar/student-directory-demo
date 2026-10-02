from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from sqlalchemy import inspect, text, update

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
    # Upgrade existing demo databases in place when new student fields are added.
    if engine.dialect.name == "sqlite":
        existing_columns = {column["name"] for column in inspect(engine).get_columns(Student.__tablename__)}
        migrations = {
            "phone": "VARCHAR(30)",
            "date_of_birth": "DATE",
            "enrollment_date": "DATE",
            "gpa": "FLOAT",
            "status": "VARCHAR(20) NOT NULL DEFAULT 'Active'",
        }
        with engine.begin() as connection:
            for column_name, column_type in migrations.items():
                if column_name not in existing_columns:
                    connection.execute(text(f"ALTER TABLE students ADD COLUMN {column_name} {column_type}"))
    # Fill the shipped fictional examples so the expanded dashboard demonstrates
    # the new fields on both fresh and already initialized demo databases.
    demo_details = {
        "asha@example.com": {"phone": "+1 202-555-0101", "date_of_birth": date(2004, 5, 14), "enrollment_date": date(2022, 8, 22), "gpa": 3.7},
        "rohan@example.com": {"phone": "+1 202-555-0102", "date_of_birth": date(2005, 2, 9), "enrollment_date": date(2023, 8, 21), "gpa": 3.4},
        "maya@example.com": {"phone": "+1 202-555-0103", "date_of_birth": date(2003, 11, 27), "enrollment_date": date(2021, 8, 23), "gpa": 3.9},
    }
    with SessionLocal() as db:
        for email, details in demo_details.items():
            for key, value in details.items():
                db.execute(
                    update(Student)
                    .where(Student.email == email, getattr(Student, key).is_(None))
                    .values(**{key: value})
                )
        db.commit()
    if seed_demo_data:
        with SessionLocal() as db:
            db.add_all(
                [
                    Student(
                        name="Asha Kumar",
                        email="asha@example.com",
                        course="Computer Science",
                        year=3,
                        phone="+1 202-555-0101",
                        date_of_birth=date(2004, 5, 14),
                        enrollment_date=date(2022, 8, 22),
                        gpa=3.7,
                    ),
                    Student(
                        name="Rohan Patel",
                        email="rohan@example.com",
                        course="Business Administration",
                        year=2,
                        phone="+1 202-555-0102",
                        date_of_birth=date(2005, 2, 9),
                        enrollment_date=date(2023, 8, 21),
                        gpa=3.4,
                    ),
                    Student(
                        name="Maya Singh",
                        email="maya@example.com",
                        course="Information Technology",
                        year=4,
                        phone="+1 202-555-0103",
                        date_of_birth=date(2003, 11, 27),
                        enrollment_date=date(2021, 8, 23),
                        gpa=3.9,
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
