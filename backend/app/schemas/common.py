from pydantic import BaseModel


class OkResponse(BaseModel):
    ok: bool = True
    message: str | None = None
