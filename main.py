from database import engine
import os
from models import Base
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseSettings
from routers import auth
from fastapi.middleware.cors import CORSMiddleware

class Settings(BaseSettings):
    authjwt_secret_key: str = os.environ.get("JWT_SECRET_KEY", "YOUR_SECRET_KEY")
    authjwt_token_location: set = {"headers"}
    authjwt_header_name: str = "Authorization"
    authjwt_header_type: str = "Bearer"


app = FastAPI()
app.include_router(auth.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",'http://192.168.0.102:3000'],  # Your React app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return Settings()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


# # Create the database tables
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created!")


if __name__ == "__main__":
    print('calling create')
    # create_tables()