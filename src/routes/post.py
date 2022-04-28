from typing import Optional

from fastapi import APIRouter, status, Path, HTTPException, Depends, Query
from fastapi.responses import Response

from src.factory import post
from src import schemas, oauth2
from src.misc import exc


router = APIRouter()


@router.get('/', status_code=status.HTTP_200_OK, response_model=list[schemas.PostSchemaOut])
async def fetch_posts(
    user: schemas.UserSchemaOut = Depends(oauth2.get_current_user),
    limit: int = Query(10), skip: int = Query(0), search: Optional[str] = ''
):
    return await post.fetch_all(user, limit=limit, skip=skip, search=search)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostSchemaOut)
async def create_post(
    payload: schemas.PostSchemaIn, user: schemas.UserSchemaOut = Depends(oauth2.get_current_user)
):
    return await post.create(payload, user)


@router.get('/{pk}', status_code=status.HTTP_200_OK)
async def fetch_post(
    pk: int = Path(...), user: schemas.UserSchemaOut = Depends(oauth2.get_current_user)
):
    try:
        return await post.fetch_by_id(pk, user)
    except exc.NotFound:
        raise HTTPException(detail='Not found', status_code=status.HTTP_404_NOT_FOUND)


@router.put('/{pk}', status_code=status.HTTP_200_OK, response_model=schemas.PostSchemaOut)
async def update_post(
    payload: schemas.PostSchemaIn, pk: int = Path(...),
    user: schemas.UserSchemaOut = Depends(oauth2.get_current_user)
):
    try:
        return await post.update(pk, payload, user)
    except exc.NotFound:
        raise HTTPException(detail='Not found', status_code=status.HTTP_404_NOT_FOUND)


@router.delete('/{pk}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    pk: int = Path(...), user: schemas.UserSchemaOut = Depends(oauth2.get_current_user)
):
    try:
        await post.destroy(pk, user)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except exc.NotFound:
        raise HTTPException(detail='Not found', status_code=status.HTTP_404_NOT_FOUND)
