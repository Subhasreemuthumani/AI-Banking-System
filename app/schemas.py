from pydantic import BaseModel

class Complaint(BaseModel):
    text: str