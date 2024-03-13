from fastapi import HTTPException
from pydantic import BaseModel
from typing import TypeVar, List

T = TypeVar('T')


class BaseAPIAdapter:
    """
    Generic base class for API adapters.
    """

    def __init__(self, repository: T):
        """Initialize the API adapter with a repository."""
        self.repo = repository

    def get_obj(self, obj_id: str) -> T:
        """Read object for matching index key from DB collection."""
        response = self.repo.read(obj_id)
        if response is None:
            raise HTTPException(
                status_code=404, detail=f"Object not found."
            )
        return response

    def create_obj(self, payload: BaseModel) -> T:
        """Create object in the collection."""
        try:
            new_obj = self.repo.create(payload)
            return new_obj
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Object creation failed: {e}")

    def read_all_obj(self) -> List[T]:
        """Read all objects from the collection."""
        return self.repo.read_all()
