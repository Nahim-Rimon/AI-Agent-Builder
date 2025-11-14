import os
import bcrypt
from jose import jwt, JWTError
from datetime import datetime, timedelta

SECRET_KEY = os.environ.get('SECRET_KEY', 'supersecretjwtkey')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_HOURS = 24

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a password against a hash."""
    try:
        # Convert to bytes
        password_bytes = plain.encode('utf-8')
        hashed_bytes = hashed.encode('utf-8')
        # Verify password
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False

def create_access_token(subject: str, expires_delta: int = None):
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS if expires_delta is None else expires_delta)
    to_encode = {'exp': expire, 'sub': subject}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get('sub')
    except JWTError:
        return None
