from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentRead, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentRead, status_code=201)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    student = Student(**payload.model_dump())
    db.add(student)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists",
        ) from exc
    return student


@router.get("", response_model=list[StudentRead])
def list_students(
    q: str | None = Query(default=None, description="Search name, email, or course"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    statement = select(Student).order_by(Student.id)
    if q and q.strip():
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(
                Student.name.ilike(pattern),
                Student.email.ilike(pattern),
                Student.course.ilike(pattern),
                Student.phone.ilike(pattern),
            )
        )
    statement = statement.offset(offset).limit(limit)
    return db.scalars(statement).all()


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.patch("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=422, detail="Provide at least one field to update")

    for key, value in changes.items():
        setattr(student, key, value)
    try:
        db.commit()
        db.refresh(student)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists",
        ) from exc
    return student


@router.delete("/{student_id}", status_code=204)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
