# BUILTIN modules
from datetime import datetime

# Third party modules
from fastapi import HTTPException, status
from bson import ObjectId
from pydantic import UUID4
from typing import List
from bson import json_util

# Local modules
from .models import (RealisationCreateModel, RealisationModel, RealisationStatus,
                     RealisationCreateInternalModel, StateUpdateSchema, NotFoundError, ConnectError)
from ..database import db, from_mongo, PyObjectId


class RealisationsRepository:
    """ This class implements the data layer adapter (the CRUD operations).
    """

    # ---------------------------------------------------------
    #
    @staticmethod
    def _read(realisation_id: str) -> RealisationModel:
        """ Read Realisation for matching index key from DB collection realisations.

        :param key: Index key.
        :return: Found Realisation.
        """

        response = from_mongo(db.realisations.find_one(
            {"_id": ObjectId(realisation_id)}))

        return RealisationModel(**response).dict()

    # ---------------------------------------------------------
    #

    def read(self, realisation_id: str) -> RealisationModel:
        """ Read Realisation for matching index key from DB collection realisations.

        :param key: Index key.
        :return: Found Realisation.
        """

        response = self._read(realisation_id=realisation_id)

        return response

    # ---------------------------------------------------------
    #

    def create(self, payload: RealisationCreateInternalModel) -> RealisationModel:
        """ Create Realisation in realisations collections.

        :param payload: New realisation payload.
        :return: Created realisation.
        """
        try:
            response = db.realisations.insert_one(payload.model_dump())
            return str(response.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail=f"Realisation creation failed. Check details provided: {payload}")

    # ---------------------------------------------------------
    #

    def read_all(self) -> List[RealisationModel]:
        """ Read Realisation in realisation collection.

        :return: list of found realisations.
        """
        response = []
        realisations = db.realisations.find({})

        for realisation in realisations:
            realisation = RealisationModel(**from_mongo(realisation)).dict()
            response.append(realisation)

        return response

    # ---------------------------------------------------------
    #

    def update(self, realisation_id: str, new_status: RealisationStatus, author_id: str) -> bool:
        """ Update Realisation in DB collection api_db.realisations.

        :param realisation_id: id of the realisation to update.
        :param new_status: The new status of the realisation.
        :param author_id: id of who make the modification
        :return: update result.
        """
        realisation = self._read(realisation_id=realisation_id)

        if realisation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NotFoundError().detail)

        # Update the update history
        update_history_entry = StateUpdateSchema(
            new_status=new_status,
            when=datetime.utcnow(),
            by=author_id)

        response = db.realisations.update_one(
            {"_id": ObjectId(realisation_id)},
            {
                "$set": {"status": new_status.value},
                "$push": {"update_history": update_history_entry.model_dump()}
            }
        )

        return response.raw_result["updatedExisting"]

    # ---------------------------------------------------------
    #

    def get_realisation_owner_id(self, realisation_id: str) -> PyObjectId:
        """ Return order status.

        :param key: Index key.
        :return: True if customer is found and False if not.
        """
        realisation = self._read(realisation_id)

        if realisation:
            return realisation.employee_id
        else:
            errmsg = f"Realisation not found: {realisation_id}."
            raise HTTPException(status_code=403, detail=errmsg)
