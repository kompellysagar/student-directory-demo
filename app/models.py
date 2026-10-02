from datetime import date
from sqlalchemy import String, Integer, Date, Float
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    course: Mapped[str] = mapped_column(String(120), index=True)
    year: Mapped[int] = mapped_column(Integer)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    enrollment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="Active", server_default="Active")
