from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import schemas, models, database
from utils import get_password_hash, verify_password
from fastapi_jwt_auth import AuthJWT
from typing import Optional

router = APIRouter()

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login_user(user_credentials: schemas.UserLogin, Authorize: AuthJWT = Depends(), db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user_credentials.username).first()
    if not db_user or not verify_password(user_credentials.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = Authorize.create_access_token(subject=db_user.username)
    refresh_token = Authorize.create_refresh_token(subject=db_user.username)
    
    # Return tokens in the response body, not in cookies
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.get("/dashboard")
def dashboard(authorization: Optional[str] = Header(None), Authorize: AuthJWT = Depends()):
    try:
        # Extract token from Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid or missing token")
        
        token = authorization.replace("Bearer ", "")
        
        # Manually decode and verify the token
        Authorize.jwt_required()  # This will set the current token from the request
        current_user = Authorize.get_jwt_subject()
        
        return {"message": f"Welcome to the dashboard, {current_user}!"}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/refresh")
def refresh_access_token(authorization: Optional[str] = Header(None), Authorize: AuthJWT = Depends()):
    try:
        # Check if refresh token is in Authorization header
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid or missing refresh token")
        
        # Set the correct authorization type for refresh tokens
        Authorize.jwt_refresh_token_required()
        current_user = Authorize.get_jwt_subject()
        new_access_token = Authorize.create_access_token(subject=current_user)
        return {"access_token": new_access_token}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))