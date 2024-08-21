from pydantic import BaseModel, Field, field_validator


class Base(BaseModel):
    id: str

    class Config:
        from_attributes = True
        populate_by_name = True

    @field_validator("id", mode="before")
    def convert_id(cls, v):
        return str(v)
