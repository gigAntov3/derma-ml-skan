from pydantic import BaseModel


class SuccessResponseSchema(BaseModel):
    ok: bool = True
    message: str = "success"