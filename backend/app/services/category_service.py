from app.core.exceptions import EntityInUseError, EntityNotFoundError
from app.core.types import DEFAULT_CATEGORY_IDS
from app.models.category import CategoryModel
from app.repositories.category_repository import CategoryRepository


class CategoryService:
    def __init__(self, repo: CategoryRepository | None = None) -> None:
        self._repo = repo or CategoryRepository()

    async def list_categories(self) -> list[CategoryModel]:
        return await self._repo.list_all()

    async def create_category(self, data: dict[str, object]) -> CategoryModel:
        return await self._repo.create(data)

    async def delete_category(self, category_id: str) -> None:
        if category_id in DEFAULT_CATEGORY_IDS:
            raise EntityInUseError(
                "Category",
                category_id,
                "default categories cannot be deleted",
            )
        deleted = await self._repo.delete(category_id)
        if not deleted:
            raise EntityNotFoundError("Category", category_id)
