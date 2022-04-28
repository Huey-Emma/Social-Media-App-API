from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.factory import auth
from src.misc import exc
from src import schemas, oauth2


router = APIRouter()


@router.post('/login', status_code=status.HTTP_201_CREATED)
async def login(payload: OAuth2PasswordRequestForm = Depends()):
    try:
        return await auth.create_access_token(payload.username, payload.password)
    except (exc.NotFound, exc.PasswordsDoNotMatch):
        raise HTTPException(detail='Invalid credentials', status_code=status.HTTP_401_UNAUTHORIZED)


@router.get('/me', status_code=status.HTTP_200_OK, response_model=schemas.UserSchemaOut)
async def fetch_me(user: schemas.UserSchemaOut = Depends(oauth2.get_current_user)):
    return user
