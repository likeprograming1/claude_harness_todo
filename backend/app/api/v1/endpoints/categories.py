from fastapi import APIRouter, Response

from app.models.category import CategoryModel
from app.schemas.category import CategoryCreate, CategoryResponse
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


def _to_response(cat: CategoryModel) -> CategoryResponse:
    return CategoryResponse(
        id=cat.mongo_id or "",
        category_id=cat.category_id,
        name=cat.name,
        color=cat.color,
        is_default=cat.is_default,
    )


@router.get("", response_model=list[CategoryResponse])
async def list_categories() -> list[CategoryResponse]:
    cats = await CategoryService().list_categories()
    return [_to_response(c) for c in cats]


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(body: CategoryCreate) -> CategoryResponse:
    cat = await CategoryService().create_category(body.model_dump())
    return _to_response(cat)


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: str) -> Response:
    await CategoryService().delete_category(category_id)
    return Response(status_code=204)
