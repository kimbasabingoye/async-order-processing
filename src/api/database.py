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
from pymongo import MongoClient
from typing import Annotated
from pydantic import BeforeValidator, BaseModel, ConfigDict
from typing import Optional, Callable, List

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
