from typing import TypeVar
from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from psycopg.rows import dict_row

from src.config import conf
from src.database import pool
from src import schemas


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def gen_access_token(payload: dict[str, object]):
    claims = {
        **payload,
        'exp': datetime.utcnow() + timedelta(days=conf.jwt_expires)
    }
    return jwt.encode(claims, conf.jwt_secret, conf.jwt_algo)


E = TypeVar('E', bound=Exception)


def verify_access_token(token: str, exception_credentials: E):
    try:
        claims = jwt.decode(token, conf.jwt_secret, [conf.jwt_algo])
    except JWTError:
        raise exception_credentials
    else:
        user_id, email = claims.get('user_id'), claims.get('email')

        if not (user_id and email):
            raise exception_credentials

        return user_id, email,


def get_current_user(token: str = Depends(oauth2_scheme)):
    exception_credentials: E = HTTPException(
        detail='Could\'t not validate credentials',
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={
            'WWW-Authenticate': 'Bearer'
        }
    )
    user_id, email = verify_access_token(token, exception_credentials)
    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        qry = 'SELECT * FROM users WHERE id = %s AND email = %s;'
        cursor.execute(qry, (user_id, email))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                detail='User for this token no longer exists.',
                status_code=status.HTTP_403_FORBIDDEN
            )
        return schemas.UserSchemaOut(**user)
