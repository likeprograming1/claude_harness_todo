import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.exceptions import EntityInUseError, EntityNotFoundError
from app.models.category import CategoryModel
from app.services.category_service import CategoryService


def _make_cat(category_id: str = "cat_custom", name: str = "My Cat") -> CategoryModel:
    return CategoryModel(
        category_id=category_id,
        name=name,
        color="#4A6FFF",
        is_default=False,
        mongo_id="abc123",
    )


def _make_svc(
    list_result: list[CategoryModel] | None = None,
    create_result: CategoryModel | None = None,
    delete_ok: bool = True,
) -> CategoryService:
    repo = MagicMock()
    repo.list_all = AsyncMock(return_value=list_result or [])
    repo.create = AsyncMock(return_value=create_result or _make_cat())
    repo.delete = AsyncMock(return_value=delete_ok)
    return CategoryService(repo=repo)


async def test_list_categories_returns_all() -> None:
    svc = _make_svc(list_result=[_make_cat("cat_custom"), _make_cat("cat_other", "Other")])
    result = await svc.list_categories()
    assert len(result) == 2


async def test_create_category_returns_model() -> None:
    cat = _make_cat()
    svc = _make_svc(create_result=cat)
    result = await svc.create_category({"name": "My Cat", "color": "#4A6FFF"})
    assert result.name == "My Cat"


async def test_delete_category_success() -> None:
    svc = _make_svc(delete_ok=True)
    await svc.delete_category("cat_custom")  # not a default → should succeed


async def test_delete_category_not_found() -> None:
    svc = _make_svc(delete_ok=False)
    with pytest.raises(EntityNotFoundError):
        await svc.delete_category("cat_missing")


@pytest.mark.parametrize("default_id", ["cat_work", "cat_personal", "cat_urgent", "cat_focus"])
async def test_delete_default_category_raises(default_id: str) -> None:
    svc = _make_svc()
    with pytest.raises(EntityInUseError):
        await svc.delete_category(default_id)
