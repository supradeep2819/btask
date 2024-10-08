from typing import Optional
from ninja import Schema




class UserSchemaOut(Schema):
    username: str
    email: str
    role: str

class LogInSchema(Schema):
    username:str
    password:str

class DetailSchema(Schema):
    detail: str


class RegisterInSchema(Schema):
    username: str
    email: str
    password: str
    role: Optional[str] = None