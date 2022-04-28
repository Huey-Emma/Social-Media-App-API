from fastapi import APIRouter, status, HTTPException, Path

from src import schemas
from src.factory import user
from src.misc import exc

router = APIRouter()


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.UserSchemaOut)
async def create_user(payload: schemas.UserSchemaIn):
    try:
        return await user.create(payload)
    except exc.DuplicateValue:
        raise HTTPException(detail='Email already in use', status_code=status.HTTP_409_CONFLICT)


@router.get('/{pk}', status_code=status.HTTP_200_OK, response_model=schemas.UserSchemaOut)
async def fetch_user(pk: int = Path(...)):
    try:
        return await user.fetch_by_id(pk)
    except exc.NotFound:
        raise HTTPException(detail='Not found', status_code=status.HTTP_404_NOT_FOUND)
