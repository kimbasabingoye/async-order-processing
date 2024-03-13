
# Third party modules
from fastapi import HTTPException
from bson import ObjectId
from pydantic import UUID4
from typing import List

# Local modules
from .models import EmployeeModel
from ..database import db, BaseRepository


class EmployeesRepository(BaseRepository[EmployeeModel]):
    def __init__(self):
        super().__init__(db, "employees")
