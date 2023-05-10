from fastapi import APIRouter

from twok.api import dependencies
from twok.database import schemas

search_router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)


# Search endpoints
@search_router.get(
    "/any/{query}",
    response_model=schemas.SearchListResponse,
)
def search_any(query: str, db: dependencies.database):
    db_results = db.search_all(query)

    return db_results


@search_router.get("/post/{query}", response_model=list[schemas.Post])
def search_post(query: str, db: dependencies.database):
    db_results = db.post.search(query)

    return db_results
