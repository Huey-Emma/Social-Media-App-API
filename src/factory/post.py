from psycopg.rows import dict_row

from src.database import pool
from src import schemas
from src.misc import exc


async def fetch_all(current_user: schemas.UserSchemaOut, **kwargs):
    limit, skip, search = kwargs.get('limit'), kwargs.get('skip'), kwargs.get('search')

    base_query = """
    SELECT posts.*, COUNT(votes.post_id) AS likes FROM posts
    LEFT JOIN votes ON votes.post_id = posts.id
    WHERE posts.published = TRUE AND posts.user_id = %s
    GROUP BY posts.id
    LIMIT %s OFFSET %s;
    """, (current_user.id, limit, skip)

    title_search_qry = """
    SELECT posts.*, COUNT(votes.post_id) AS likes FROM posts
    LEFT JOIN votes ON votes.post_id = posts.id
    WHERE posts.published = TRUE AND posts.user_id = %s AND posts.title ILIKE %s
    GROUP BY posts.id
    LIMIT %s OFFSET %s;
    """, (current_user.id, f'%{search}%', limit, skip)

    query_selector = {
        True: lambda: base_query,
        not not search: lambda: title_search_qry
    }[True]

    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        qry, opts = query_selector()
        cursor.execute(qry, opts)
        posts = cursor.fetchall()
        return [schemas.PostSchemaOut(**post) for post in posts]


async def create(payload: schemas.PostSchemaIn, current_user: schemas.UserSchemaOut):
    qry = 'INSERT INTO posts (title, content, published, user_id) VALUES (%s, %s, %s, %s) RETURNING *;'

    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(qry, (payload.title, payload.content, payload.published, current_user.id))
        post = cursor.fetchone()
        return schemas.PostSchemaOut(**post)


async def fetch_by_id(pk: int, current_user: schemas.UserSchemaOut):
    qry = """
    SELECT posts.*, users.username, users.email, users.id AS id_user, 
    users.created AS user_created,
    COUNT(votes.post_id) AS likes
    FROM posts LEFT JOIN votes ON votes.post_id = posts.id
    INNER JOIN users ON users.id = posts.user_id
    WHERE posts.id = %s AND posts.user_id = %s
    GROUP BY posts.id, users.id
    """

    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(qry, (pk, current_user.id))
        post = cursor.fetchone()

        if not post:
            raise exc.NotFound

        return schemas.PostUserSchemaOut(**post | {
            'user': {
                'id': post.pop('id_user'),
                'username': post.pop('username'),
                'email': post.pop('email'),
                'created': post.pop('user_created')
            }
        })


async def update(pk: int, payload: schemas.PostSchemaIn, current_user: schemas.UserSchemaOut):
    qry = """
    UPDATE posts 
    SET title = %s, content = %s, published = %s, updated = NOW()
    WHERE id = %s AND user_id = %s RETURNING *;
    """

    with pool.connection() as conn:
        cursor = conn.cursor(row_factory=dict_row)
        cursor.execute(qry, (
            payload.title, payload.content, payload.published, pk, current_user.id))
        post = cursor.fetchone()
        if not post:
            raise exc.NotFound
        return schemas.PostSchemaOut(**post)


async def destroy(pk: int, current_user: schemas.UserSchemaOut):
    qry = 'DELETE FROM posts WHERE id = %s AND user_id = %s RETURNING *;'

    with pool.connection() as conn:
        cursor = conn.cursor()
        cursor.execute(qry, (pk, current_user.id))
        post = cursor.fetchone()
        if not post:
            raise exc.NotFound
