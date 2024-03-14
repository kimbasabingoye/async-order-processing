# BUILTIN modules
from datetime import datetime

# Third party modules
from fastapi import HTTPException, status
from bson import ObjectId
from pydantic import UUID4
from typing import List, Optional
from bson import json_util
from loguru import logger

# Local modules
from .models import (QuotationModel, QuotationStatus,
                     QuotationCreateInternalModel, StateUpdateSchema, NotFoundError)
from ..database import db, from_mongo, PyObjectId


class QuotationsRepository:
    """ This class implements the data layer adapter (the CRUD operations).
    """

    # ---------------------------------------------------------
    #
    @staticmethod
    def _read(quotation_id: str) -> QuotationModel:
        """ Read Quotation for matching index key from DB collection quotations.

        :param key: Index key.
        :return: Found Quotation.
        """

        response = from_mongo(db.quotations.find_one(
            {"_id": ObjectId(quotation_id)}))

        return QuotationModel(**response).dict()

    # ---------------------------------------------------------
    #

    def read(self, quotation_id: str) -> QuotationModel:
        """ Read Quotation for matching index key from DB collection quotations.

        :param key: Index key.
        :return: Found Quotation.
        """

        response = self._read(quotation_id=quotation_id)

        return response



    # ---------------------------------------------------------
    #

    def create(self, payload: QuotationCreateInternalModel) -> PyObjectId:
        """ Create Quotation in quotations collections.

        :param payload: New quotation payload.
        :return: Created quotation id.
        """
        try:
            response = db.quotations.insert_one(payload.model_dump())
            return str(response.inserted_id)
        except Exception as e:
            raise HTTPException(status_code=500,
                                detail=f"Quotation creation failed. Check details provided: {payload}")

    # ---------------------------------------------------------
    #

    def read_all(self) -> List[QuotationModel]:
        """ Read Quotation in quotation collection.

        :return: list of found quotations.
        """
        response = []
        quotations = db.quotations.find({})

        for quotation in quotations:
            quotation = QuotationModel(**from_mongo(quotation)).dict()
            response.append(quotation)

        return response

    # ---------------------------------------------------------
    #

    def update(self, quotation_id: str, new_status: QuotationStatus, author_id: str) -> bool:
        """ Update Quotation in DB collection api_db.quotations.

        :param quotation_id: id of the quotation to update.
        :param new_status: The new status of the quotation.
        :param author_id: id of who make the modification
        :return: result of update.
        """
        quotation = self._read(quotation_id=quotation_id)

        if quotation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=NotFoundError().detail)

        # Update the update history
        update_history_entry = StateUpdateSchema(
            new_status=new_status,
            when=datetime.utcnow(),
            by=author_id)

        response = db.quotations.update_one(
            {"_id": ObjectId(quotation_id)},
            {
                "$set": {"status": new_status.value},
                "$push": {"update_history": update_history_entry.model_dump()}
            }
        )

        return response.raw_result['updatedExisting']
    
    # ---------------------------------------------------------
    #

    def get_status(quotation_id: PyObjectId) -> QuotationStatus:
        """Get the status of a quotation.

        :param quotation_id: The ID of the quotation.
        :return: The status of the quotation.
        """
        # Query the database to find the quotation with the specified quotation_id
        quotation = db.quotations.find_one({"_id": ObjectId(quotation_id)})

        if quotation:
            # Extract the status from the quotation document
            status = quotation.get("status")

            # Return the QuotationStatus enum corresponding to the status
            return QuotationStatus(status)

        # If quotation is not found, return None or raise an exception based on your requirement
        return None
    
    # ---------------------------------------------------------
    #
    @staticmethod
    def read_accepted_quotation_for_order(order_id: PyObjectId) -> Optional[PyObjectId]:
        """Get the ID of the accepted quotation associated with the specified order.

        :param order_id: The ID of the order.
        :return: The ID of the accepted quotation if found, None otherwise.
        """
        # Query the database to find the accepted quotation associated with the specified order
        accepted_quotation = db.quotations.find_one({"order_id": order_id, "status": QuotationStatus.QACC.value})

        logger.debug(f"Accepted Quotation: {accepted_quotation}")

        if accepted_quotation:
            # Extract the ID of the accepted quotation
            accepted_quotation_id = accepted_quotation.get("_id")
            return accepted_quotation_id

        return None
    
    # ---------------------------------------------------------
    #
    def is_accepted(self, quotation_id: PyObjectId) -> bool:
        """Check if a quotation is accepted.

        :param quotation_id: The ID of the quotation to check.
        :return: True if the quotation is accepted, False otherwise.
        """
        # Get the status of the quotation
        status = self.get_status(quotation_id)

        # Check if the status is QuotationStatus.ACCEPTED
        return status == QuotationStatus.QACC
    
    # ---------------------------------------------------------
    #

    def read_order_quotations(self, order_id: PyObjectId) -> List[QuotationModel]:
        """ Read Quotations for matching order id key from DB collection quotations.

        :param order_id: the order id.
        :return: Found Quotations.
        """

        response = db.quotations.find(
            {"order_id": order_id})

        # if response is None:
        #    return []

        quotations = []

        for quotation in response:
            quotation = QuotationModel(**from_mongo(quotation)).dict()
            quotations.append(quotation)
        return quotations
    
    # ---------------------------------------------------------
    #

    def have_accepted_quotation(self, order_id: PyObjectId) -> bool:
        """Check if the order has an accepted quotation.

        :return: True if the order has an accepted quotation, False otherwise.
        """

        # Read the accepted quotation associated with the current order
        order_quotation = self.read_accepted_quotation_for_order(order_id)

        # Check if an accepted quotation is found
        if order_quotation is not None:
            return True

        return False

