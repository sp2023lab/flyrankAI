from pydantic import BaseModel, field_validator


class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be empty")
        return value


class TaskUpdate(BaseModel):
    title: str
    done: bool

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be empty")
        return value


class Task(BaseModel):
    id: int
    title: str
    done: bool
