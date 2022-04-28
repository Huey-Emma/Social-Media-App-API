from fastapi import APIRouter, status, Depends, HTTPException
from psycopg import errors

from src import schemas, oauth2
from src.factory import vote
from src.misc import exc


router = APIRouter()


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_vote(
    payload: schemas.VoteSchemaIn,
    user: schemas.UserSchemaOut = Depends(oauth2.get_current_user)
):
    try:
        return await vote.create(payload, user)
    except exc.NotFound:
        raise HTTPException(detail='Vote does not exist', status_code=status.HTTP_404_NOT_FOUND)
    except exc.DuplicateValue:
        raise HTTPException(detail='Vote already exists', status_code=status.HTTP_409_CONFLICT)
    except errors.ForeignKeyViolation:
        raise HTTPException(detail='Post does not exist', status_code=status.HTTP_404_NOT_FOUND)
