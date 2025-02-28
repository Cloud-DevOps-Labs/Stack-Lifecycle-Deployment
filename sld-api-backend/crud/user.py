import bcrypt
import sys
from sqlalchemy.orm import Session
from sqlalchemy import exc
import datetime

from security.vault import vault_encrypt, vault_decrypt
from security.tokens import get_password_hash
from config.api import settings
import db.models as models
import schemas.schemas as schemas
import logging

logging.getLogger("uvicorn.error").propagate = False
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

hashing_passwd = get_password_hash


@vault_encrypt
def encrypt(secreto):
    try:
        return secreto
    except Exception as err:
        raise err


@vault_decrypt
def decrypt(secreto):
    try:
        return secreto
    except Exception as err:
        raise err


def is_active(db: Session, user: schemas.UserCreate) -> bool:
    try:
        return user.is_active
    except Exception as err:
        raise err


def is_superuser(db: Session, user: schemas.UserCreate) -> bool:
    try:
        return user.privilege
    except Exception as err:
        raise err


def is_master(db: Session, user: schemas.UserCreate) -> bool:
    try:
        return user.master
    except Exception as err:
        raise err


def get_user_by_username(db: Session, username: str):
    try:
        return db.query(
            models.User).filter(
            models.User.username == username).first()
    except Exception as err:
        raise err


def get_user_by_id(db: Session, id: int):
    try:
        return db.query(models.User).filter(models.User.id == id).first()
    except Exception as err:
        raise err

def get_user_by_username_squad(db: Session, username: str):
    try:
        return db.query(
            models.User).filter(
            models.User.username == username).filter(models.User.squad == squad).first()
    except Exception as err:
        raise err


def get_user_by_id_squad(db: Session, id: int):
    try:
        return db.query(models.User).filter(models.User.id == id).filter(models.User.squad == squad).first()
    except Exception as err:
        raise err


def get_users_by_squad(db: Session, squad: str, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.User).filter(models.User.squad == squad).offset(skip).limit(limit).all()
    except Exception as err:
        raise err

def get_users(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(models.User).offset(skip).limit(limit).all()
    except Exception as err:
        raise err

def create_init_user(db: Session, password: str):
    db_user = models.User(username=settings.INIT_USER.get("username"),
                          fullname=settings.INIT_USER.get("fullname"),
                          email=settings.INIT_USER.get("email"),
                          squad="master",
                          privilege=True,
                          master=True,
                          is_active=True,
                          created_at=datetime.datetime.now(),
                          password=hashing_passwd(password))
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as err:
        raise err


def create_user(db: Session, user: schemas.UserCreate, squad: str):
    db_user = models.User(**user.dict())
    db_user.password = hashing_passwd(user.password)
    db_user.created_at = datetime.datetime.now()
    db_user.squad = squad
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except exc.IntegrityError as err:
        raise ValueError(str(err.__dict__['orig']))
    except Exception as err:
        raise err


def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(
        models.User.id == user_id).first()
    db_user.updated_at = datetime.datetime.now()
    check_None = [None, "", "string"]
    if user.password not in check_None:
        db_user.password = hashing_passwd(user.password)
    if user.username not in check_None:
        db_user.username = user.username
    if user.email not in check_None:
        db_user.email = user.email
    if user.fullname not in check_None:
        db_user.fullname = user.fullname
    if user.squad not in check_None:
        db_user.squad = user.squad
    if user.privilege not in check_None:
        db_user.privilege = user.privilege
    if user.is_active not in check_None:
        db_user.is_active = user.is_active
    if user.master not in check_None:
        db_user.master = user.master
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as err:
        raise err

def password_reset(db: Session, user_id: int, password: schemas.PasswordReset):
    db_user = db.query(models.User).filter(
        models.User.id == user_id).first()
    db_user.updated_at = datetime.datetime.now()

    check_None = [None, "", "string"]
    if password not in check_None:
        db_user.password = hashing_passwd(password.passwd)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as err:
        raise err


def delete_user_by_id(db: Session, id: int):
    db.query(models.User).filter(
        models.User.id == id).delete()
    try:
        db.commit()
        return {id: "deleted"}
    except Exception as err:
        raise err


def delete_user_by_name(db: Session, username: str):
    db.query(models.User).filter(
        models.User.username == username).delete()
    try:
        db.commit()
        return {username: "deleted"}
    except Exception as err:
        raise err


def check_username_password(db: Session, user: schemas.UserAuthenticate):
    db_user_info: models.User = get_user_by_username(
        db, username=user.username)
    try:
        return bcrypt.checkpw(
            user.password.encode('utf-8'),
            db_user_info.password.encode('utf-8'))
    except Exception as err:
        raise err
