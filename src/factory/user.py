from psycopg.rows import dict_row

from src.database import pool
from src import schemas
from src.misc import exc, hash


async def create(payload: schemas.UserSchemaIn):
    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)

        qry = 'SELECT email FROM users WHERE email = %s;'
        cursor.execute(qry, (payload.email,))
        user_exists = cursor.fetchone() is not None
        if user_exists:
            raise exc.DuplicateValue

        qry = 'INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING *;'
        cursor.execute(qry, (payload.username, payload.email, hash.get(payload.password)))
        user = cursor.fetchone()
        return schemas.UserSchemaOut(**user)


async def fetch_by_id(pk: int):
    qry = 'SELECT * FROM users WHERE id = %s;'

    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(qry, (pk,))
        user = cursor.fetchone()
        if not user:
            raise exc.NotFound
        return schemas.UserSchemaOut(**user)
