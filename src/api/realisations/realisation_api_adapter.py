
from datetime import datetime
import json

# Third party modules
from fastapi import HTTPException
from pydantic import UUID4
from typing import List

# Local modules
from .realisation_data_adapter import RealisationsRepository
from .models import RealisationCreateModel, RealisationModel
from .realisation_api_logic import RealisationApiLogic


# ------------------------------------------------------------------------
#
class RealisationsApi:
    """
    This class implemnts the Web API layer adapter.
    """

    # ---------------------------------------------------------
    #
    def __init__(self, repository: RealisationsRepository):
        """ The class initializer.

        :param repository: Data layer handler object
        """
        self.repo = repository

    # ---------------------------------------------------------
    #
    def _realisation_of(self, realisation_id: str) -> RealisationModel:
        """ Return specified realisation.

        :param realisation_id: realisation id for realisation to find.
        :return: Found realisation object.
        :raise HTTPException [404]: when realisation not found in DB.
        """
        db_realisation = self.repo.read(realisation_id)

        if not db_realisation:
            errmsg = f"{realisation_id} not found in DB api_db.realisations"
            raise HTTPException(status_code=404, detail=errmsg)

        return db_realisation

    # ---------------------------------------------------------
    #

    def get_realisation(self, realisation_id: str) -> RealisationModel:
        """ Return specified realisation. 

        :param realisation_id: realisation id for realisation to find.
        :return: Found realisation object.
        :raise HTTPException [404]: when realisation not found in DB api_db.realisations.
        """
        db_realisation = self._realisation_of(realisation_id)

        return db_realisation

    # ---------------------------------------------------------
    #

    def create_realisation(self, payload: RealisationCreateModel) -> RealisationModel:
        """ Create a new realisation in DB.

        :param payload: realisation payload.
        :return: Created realisation object.
        :raise HTTPException [400]: when create realisation in DB api_db.realisations failed.
        """
        # print(f"############## {payload} #################")
        # print(type(payload))

        service = RealisationApiLogic(
            repository=self.repo,
            **payload
        )
        return service.create()

    # ---------------------------------------------------------
    #

    def list_realisations(self) -> List[RealisationModel]:
        """ list all existing realisations in DB api_db.realisations.

        :return: list of found realisations
        """

        db_realisations = self.repo.read_all()

        return db_realisations

    # ---------------------------------------------------------
    #

    def cancel_realisation(self, realisation_id: str, author_id: str) -> RealisationModel:
        """ Cancel specified realisation (will be done by customer).

        :param realisation_id: id for realisation to cancel.
        :return: Found Realisation object.
        :raise HTTPException [400]: when failed to update DB api_db.realisations.
        :raise HTTPException [404]: when Realisation not found in DB api_db.realisations.
        """

        # _realisation_of raise exception if the realisation is not found
        db_realisation = self._realisation_of(realisation_id)

        realisation = RealisationApiLogic(
            repository=self.repo,
            author_id=author_id,
            **db_realisation)
        return realisation.cancel()
    # ---------------------------------------------------------
    #

    def start_realisation(self, realisation_id: str, author_id: str) -> RealisationModel:
        """ Start specified realisation (will be done by employee).

        :param realisation_id: id for realisation to cancel.
        :return: Found Realisation object.
        :raise HTTPException [400]: when failed to update DB api_db.realisations.
        :raise HTTPException [404]: when Realisation not found in DB api_db.realisations.
        """

        # _realisation_of raise exception if the realisation is not found
        db_realisation = self._realisation_of(realisation_id)

        realisation = RealisationApiLogic(
            repository=self.repo,
            author_id=author_id,
            **db_realisation)
        return realisation.start()

    # ---------------------------------------------------------
    #

    def complete_realisation(self, realisation_id: str, author_id: str) -> RealisationModel:
        """ Complete specified realisation (will be done by customer).

        :param realisation_id: id for realisation to refuse.
        :return: Found Realisation object.
        :raise HTTPException [400]: when failed to update DB api_db.realisations.
        :raise HTTPException [404]: when Realisation not found in DB api_db.realisations.
        """

        # _realisation_of raise exception if the realisation is not found
        db_realisation = self._realisation_of(realisation_id)

        realisation = RealisationApiLogic(
            repository=self.repo,
            author_id=author_id,
            **db_realisation)
        return realisation.complete()
