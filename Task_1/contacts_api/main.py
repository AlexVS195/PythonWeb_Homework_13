from fastapi import FastAPI, Depends, HTTPException, APIRouter, status, Security
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from src.database.db import engine, get_db
from src.schemas import ContactCreate, Contact, UserModel, UserResponse, TokenModel
from crud import add_contact, get_contacts, get_contact, refresh_contact, remove_contact, get_upcoming_birthdays
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.database.models import Base, User


app = FastAPI()

# Database initialization
Base.metadata.create_all(bind=engine)

# Create contact
@app.post("/contacts/", response_model=Contact, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    return add_contact(db=db, contact=contact, user=current_user)

# Read contacts
@app.get("/contacts/", response_model=List[Contact])
def read_contacts(
    skip: int = 0, limit: int = 10, query: str = None, db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    return get_contacts(db=db, skip=skip, limit=limit, query=query, user=current_user)

# Read contact by ID
@app.get("/contacts/{contact_id}", response_model=Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db), 
                 current_user: User = Depends(auth_service.get_current_user)):
    db_contact = get_contact(db=db, contact_id=contact_id, user=current_user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

# Update contact
@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact: ContactCreate, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    db_contact = get_contact(db=db, contact_id=contact_id, user=current_user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return refresh_contact(db=db, contact_id=contact_id, contact=contact, user=current_user)

# Delete contact
@app.delete("/contacts/{contact_id}", response_model=Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db),
                   current_user: User = Depends(auth_service.get_current_user)):
    db_contact = get_contact(db=db, contact_id=contact_id, user=current_user)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return remove_contact(db=db, contact_id=contact_id, user=current_user)

# Get contacts with upcoming birthdays
@app.get("/contacts/upcoming_birthdays/", response_model=List[Contact])
def get_upcoming_birthdays_list(db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    return get_upcoming_birthdays(db=db, user=current_user)


security = HTTPBearer()

@app.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}


@app.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}