from psycopg.rows import dict_row

from src import oauth2
from src.misc import exc, hash
from src.database import pool


async def create_access_token(email: str, password: str):
    qry = 'SELECT * FROM users WHERE email = %s;'

    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(qry, (email,))
        user = cursor.fetchone()

        if not user:
            raise exc.NotFound

        if not hash.verify(password, user['password']):
            raise exc.PasswordsDoNotMatch

        access_token = oauth2.gen_access_token({
            'user_id': user['id'],
            'email': user['email']
        })

        return {
            'access_token': access_token,
            'token_type': 'Bearer'
        }
