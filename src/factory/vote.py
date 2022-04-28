from psycopg.rows import dict_row

from src import schemas
from src.database import pool
from src.misc import exc


def upvote(payload: schemas.VoteSchemaIn, user: schemas.UserSchemaOut):
    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        qry = 'SELECT * FROM votes WHERE post_id = %s AND user_id = %s;'
        cursor.execute(qry, (payload.post_id, user.id))
        vote_exists = cursor.fetchone() is not None
        if vote_exists:
            raise exc.DuplicateValue
        qry = 'INSERT INTO votes (post_id, user_id) VALUES (%s, %s);'
        cursor.execute(qry, (payload.post_id, user.id))
        return {'status': 'success'}


def down_vote(payload: schemas.VoteSchemaIn, user: schemas.UserSchemaOut):
    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        qry = 'SELECT * FROM votes WHERE post_id = %s AND user_id = %s;'
        cursor.execute(qry, (payload.post_id, user.id))
        vote_does_not_exist = cursor.fetchone() is None
        if vote_does_not_exist:
            raise exc.NotFound
        qry = 'DELETE FROM votes WHERE post_id = %s AND user_id = %s;'
        cursor.execute(qry, (payload.post_id, user.id))
        return {'status': 'success'}


async def create(payload: schemas.VoteSchemaIn, user: schemas.UserSchemaOut):
    vote_selector = {
        payload.direction == 1: upvote,
        payload.direction == 0: down_vote
    }[True]
    return vote_selector(payload, user)

