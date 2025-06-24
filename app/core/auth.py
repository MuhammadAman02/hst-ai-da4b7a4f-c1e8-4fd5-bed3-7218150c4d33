"""Authentication and authorization management"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db, User
from app.core.logger import app_logger

class AuthManager:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.current_user: Optional[User] = None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def register_user(self, db: Session, username: str, email: str, password: str, full_name: str = None) -> User:
        """Register a new user"""
        hashed_password = self.get_password_hash(password)
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def is_admin(self) -> bool:
        """Check if current user is admin"""
        return self.current_user and self.current_user.is_admin
    
    def login(self, user: User):
        """Log in a user"""
        self.current_user = user
        app_logger.info(f"User {user.username} logged in")
    
    def logout(self):
        """Log out current user"""
        if self.current_user:
            app_logger.info(f"User {self.current_user.username} logged out")
        self.current_user = None