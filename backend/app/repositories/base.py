from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection

from app.core.database import get_db

T = TypeVar("T")


def _id_to_str(value: Any) -> str:
    """Convert MongoDB _id (ObjectId or any type) to a plain str."""
    if isinstance(value, ObjectId):
        return str(value)
    return str(value)


class BaseRepository(ABC, Generic[T]):
    collection_name: str = ""

    def _col(self) -> AsyncIOMotorCollection[dict[str, Any]]:
        return get_db()[self.collection_name]

    @abstractmethod
    def _doc_to_model(self, doc: dict[str, Any]) -> T: ...
