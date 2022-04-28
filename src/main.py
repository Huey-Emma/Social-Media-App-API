import fastapi
from fastapi.middleware.cors import CORSMiddleware

from src.database import pool
from src.routes import post, user, auth, vote


app = fastapi.FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=['*'],
    allow_methods=['*']
)


@app.on_event('startup')
def open_pool():
    pool.open()


app.include_router(post.router, tags=['Post'], prefix='/api/posts')
app.include_router(user.router, tags=['User'], prefix='/api/users')
app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(vote.router, tags=['Vote'], prefix='/api/votes')


@app.on_event('shutdown')
def close_pool():
    pool.close()
