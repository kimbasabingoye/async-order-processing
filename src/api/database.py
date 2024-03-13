# -*- coding: utf-8 -*-
"""
Copyright: Wilde Consulting
  License: Apache 2.0

VERSION INFO::
    $Repo: fastapi_mongo
  $Author: Anders Wiklund
    $Date: 2023-02-28 19:26:05
     $Rev: 52
"""

# Third party modules
from typing import List, TypeVar, Generic
from bson import ObjectId
from fastapi import HTTPException
from pymongo import MongoClient
from typing import Annotated
from pydantic import BeforeValidator
from typing import  List

# Local program modules
from ..config.setup import config

client = MongoClient(config.mongo_url)

db = client.get_database("AsyncOrderProcDB")

PyObjectId = Annotated[str, BeforeValidator(str)]


# ------------------------------------------------------------------------
#
def from_mongo(data: dict):
    """ Convert "_id" (str object) into "id" str. """

    if not data:
        return data

    if '_id' in data:
        data['id'] = str(data.pop('_id'))
        return data


# Define a generic model type
T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Generic base class for repository operations."""

    def __init__(self, db, collection_name: str):
        self.db = db
        self.collection_name = collection_name
        self.collection = db[collection_name]

    def _read(self, obj_id: str) -> T:
        """Read object for matching index key from DB collection."""
        response = self.collection.find_one({"_id": ObjectId(obj_id)})
        return from_mongo(response) if response else None

    def check_exists(self, obj_id: str) -> bool:
        """Check if the object exists."""
        return self._read(obj_id) is not None

    def read(self, obj_id: str) -> T:
        """Read object for matching index key from DB collection."""
        return self._read(obj_id)

    def create(self, payload: dict) -> str:
        """Create object in the collection."""
        try:
            new_obj = self.collection.insert_one(payload)
            return str(new_obj.inserted_id)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Object creation failed: {e}")

    def read_all(self) -> List[T]:
        """Read all objects from the collection."""
        return list(map(from_mongo, self.collection.find({})))
    
    def delete(self, obj_id: str) -> bool:
        """Delete object from the collection."""
        try:
            result = self.collection.delete_one({"_id": ObjectId(obj_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to delete object: {e}")
