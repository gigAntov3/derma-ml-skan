from typing import List
from pydantic import BaseModel


class CookieSettings(BaseModel):
    """Cookie settings"""

    httponly: bool = True
    secure: bool = False
    samesite: str = "lax"
    path: str = "/"
    max_age: int = 7 * 24 * 60 * 60