from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from datetime import date
from typing import Literal


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    course: str = Field(min_length=1, max_length=120)
    year: int = Field(ge=1, le=10)
    phone: str | None = Field(default=None, max_length=30)
    date_of_birth: date | None = None
    enrollment_date: date | None = None
    gpa: float | None = Field(default=None, ge=0, le=4)
    status: Literal["Active", "Graduated", "On leave"] = "Active"

    @field_validator("name", "course")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @field_validator("phone")
    @classmethod
    def clean_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        return value or None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email: EmailStr | None = None
    course: str | None = Field(default=None, min_length=1, max_length=120)
    year: int | None = Field(default=None, ge=1, le=10)
    phone: str | None = Field(default=None, max_length=30)
    date_of_birth: date | None = None
    enrollment_date: date | None = None
    gpa: float | None = Field(default=None, ge=0, le=4)
    status: Literal["Active", "Graduated", "On leave"] | None = None

    @field_validator("name", "course")
    @classmethod
    def clean_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank")
        return value

    @field_validator("email")
    @classmethod
    def normalize_optional_email(cls, value: EmailStr | None) -> str | None:
        if value is None:
            return value
        return str(value).strip().lower()

    @field_validator("phone")
    @classmethod
    def clean_optional_phone(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def reject_null_updates(self):
        nullable_fields = {"phone", "date_of_birth", "enrollment_date", "gpa"}
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None and field_name not in nullable_fields:
                raise ValueError(f"{field_name} cannot be null")
        return self


class StudentRead(StudentCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be blank")
        return value


class ChatResponse(BaseModel):
    answer: str
    mode: str
