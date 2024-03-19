from pydantic import BaseModel

class FitInfo(BaseModel):
    accountId: str
    token: str