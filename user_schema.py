from pydantic import BaseModel

class NewUserForm(BaseModel):
    id: str
    password: str


