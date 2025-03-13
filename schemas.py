from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    username: str
    
class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(UserBase):
    password: str
    email: str  # Change to EmailStr for better validation if you want

class User(UserBase):
    id: int
    email: str
    
    class Config:
        orm_mode = True  # To enable ORM model conversion