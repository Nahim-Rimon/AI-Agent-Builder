from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import schemas, models, utils, database
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Body

router = APIRouter(tags=['auth'])

@router.post('/register', response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter((models.User.email == user.email)|(models.User.username == user.username)).first()
    if existing:
        raise HTTPException(status_code=400, detail='User already exists')
    hashed = utils.hash_password(user.password)
    u = models.User(username=user.username, email=user.email, password=hashed)
    db.add(u); db.commit(); db.refresh(u)
    return u

@router.post('/login', response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not utils.verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    token = utils.create_access_token(user.email)
    return {'access_token': token, 'token_type': 'bearer'}
