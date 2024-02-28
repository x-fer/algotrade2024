from pydantic import BaseModel


class SuccessfulResponse(BaseModel):
    successful: bool = True
