from pydantic import BaseModel, Field, field_validator
import re


class User(BaseModel):
    name: str
    id: int
    age: int
    is_adult: bool

class Feedback(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    message: str = Field(..., min_length=10, max_length=500)

    @field_validator("message")
    @classmethod
    def no_bad_words(cls, v: str) -> str:
        bad_roots = ["кринж", "рофл", "вайб"]

        text = v.lower()

        for root in bad_roots:
            pattern = rf"(^|[^\w]){re.escape(root)}\w*($|[^\w])"
            if re.search(pattern, text, flags=re.IGNORECASE):
                raise ValueError("Использование недопустимых слов")

        return v
