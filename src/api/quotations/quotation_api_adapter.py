
from datetime import datetime
import json

# Third party modules
from fastapi import HTTPException
from pydantic import UUID4
from typing import List

# Local modules
from .quotation_data_adapter import QuotationsRepository
from .models import QuotationCreateModel, QuotationModel
from .quotation_api_logic import QuotationApiLogic


# ------------------------------------------------------------------------
#
class QuotationsApi:
    """
    This class implemnts the Web API layer adapter.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: QuotationsRepository):
        """ The class initializer.

        :param repository: Data layer handler object
        """
        self.repo = repository

    # ---------------------------------------------------------
    #
    def _quotation_of(self, quotation_id: str) -> QuotationModel:
        """ Return specified quotation.

        :param quotation_id: quotation id for quotation to find.
        :return: Found quotation object.
        :raise HTTPException [404]: when quotation not found in DB.
        """
        db_quotation = self.repo.read(quotation_id)

        if not db_quotation:
            errmsg = f"{quotation_id} not found in DB api_db.quotations"
            raise HTTPException(status_code=404, detail=errmsg)

        return db_quotation

    # ---------------------------------------------------------
    #

    def get_quotation(self, quotation_id: str) -> QuotationModel:
        """ Return specified quotation. 

        :param quotation_id: quotation id for quotation to find.
        :return: Found quotation object.
        :raise HTTPException [404]: when quotation not found in DB api_db.quotations.
        """
        db_quotation = self._quotation_of(quotation_id)

        return db_quotation

    # ---------------------------------------------------------
    #

    def create_quotation(self, payload: QuotationCreateModel) -> QuotationModel:
        """ Create a new quotation in DB.

        :param payload: quotation payload.
        :return: Created quotation object.
        :raise HTTPException [400]: when create quotation in DB api_db.quotations failed.
        """
        #print(f"############## {payload} #################")
        # print(type(payload))


        service = QuotationApiLogic(
            repository=self.repo,
            **payload
        )
        return service.create()

    # ---------------------------------------------------------
    #

    def list_quotations(self) -> List[QuotationModel]:
        """ list all existing quotations in DB api_db.quotations.

        :return: list of found quotations
        """

        db_quotations = self.repo.read_all()

        return db_quotations

    # ---------------------------------------------------------
    #

    def cancel_quotation(self, quotation_id: str, author_id: str) -> QuotationModel:
        """ Cancel specified quotation (will be done by customer).

        :param quotation_id: id for quotation to cancel.
        :return: Found Quotation object.
        :raise HTTPException [400]: when failed to update DB api_db.quotations.
        :raise HTTPException [404]: when Quotation not found in DB api_db.quotations.
        """

        # _quotation_of raise exception if the quotation is not found
        db_quotation = self._quotation_of(quotation_id)

        quotation = QuotationApiLogic(
            repository=self.repo,
            update_id=author_id,
            **db_quotation)
        return quotation.cancel()
    # ---------------------------------------------------------
    #

    def validate_quotation(self, quotation_id: str, author_id: str) -> QuotationModel:
        """ Validate specified quotation (will be done by employee).

        :param quotation_id: id for quotation to cancel.
        :return: Found Quotation object.
        :raise HTTPException [400]: when failed to update DB api_db.quotations.
        :raise HTTPException [404]: when Quotation not found in DB api_db.quotations.
        """

        # _quotation_of raise exception if the quotation is not found
        db_quotation = self._quotation_of(quotation_id)

        quotation = QuotationApiLogic(
            repository=self.repo,
            updater_id=author_id,
            **db_quotation)
        return quotation.validate()

     # ---------------------------------------------------------
    #

    def reject_quotation(self, quotation_id: str, author_id: str) -> QuotationModel:
        """ Reject specified quotation (will be done by customer).

        :param quotation_id: id for quotation to refuse.
        :return: Found Quotation object.
        :raise HTTPException [400]: when failed to update DB api_db.quotations.
        :raise HTTPException [404]: when Quotation not found in DB api_db.quotations.
        """

        # _quotation_of raise exception if the quotation is not found
        db_quotation = self._quotation_of(quotation_id)

        quotation = QuotationApiLogic(
            repository=self.repo,
            updater_id=author_id,
            **db_quotation)
        return quotation.reject()

    # ---------------------------------------------------------
    #

    def accept_quotation(self, quotation_id: str, author_id: str) -> QuotationModel:
        """ Accept specified quotation (will be done by customer).

        :param quotation_id: id for quotation to accept.
        :return: Found Quotation object.
        :raise HTTPException [400]: when failed to update DB api_db.quotations.
        :raise HTTPException [404]: when Quotation not found in DB api_db.quotations.
        """

        # _quotation_of raise exception if the quotation is not found
        db_quotation = self._quotation_of(quotation_id)

        quotation = QuotationApiLogic(
            repository=self.repo,
            updater_id=author_id,
            **db_quotation)
        return quotation.accept()
