from pydantic import BaseModel


class SuccessfulResponse(BaseModel):
    successful: bool = True
    message: str = "Operation done successfully"
