from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def get(plain_pwd: str):
    return pwd_context.hash(plain_pwd)


def verify(plain_pwd: str, pwd_hash: str):
    return pwd_context.verify(plain_pwd, pwd_hash)
