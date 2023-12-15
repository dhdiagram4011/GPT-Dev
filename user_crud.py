from sqlalchemy.orm import Session

from models import User
from user.user_schema import NewUserForm
from passlib.context import CryptContext

pwd_context = CryptContext(schema=["bcrypt"], deprecated="auto")



def get_user(id:str, db: Session):
    return db.query(User).filter(User.id == id().first())


def create_user(new_user: NewUserForm, db: Session):
    user = User(
        id = new_user.name,
        hashed_pw = pwd_context.hash(new_user.password)
    )
    db.add(user)
    db.commit()


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

