import sys
import os
# Add the project's root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

from src.api.orders.models import (OrderCreateInternalModel,
                                   OrderModel, OrderStatus,
                                   NotFoundError, StateUpdateSchema)
from src.api.database import db
from src.api.orders.order_data_adapter import OrdersRepository
from fastapi import HTTPException, status
from bson import ObjectId
from datetime import datetime
from unittest.mock import patch, MagicMock
import unittest





class TestOrdersRepository(unittest.TestCase):
    def setUp(self):
        # Initialize the repository
        self.repository = OrdersRepository()

    def test_read_order_quotations(self):
        # Mock the database response
        expected_quotations = [
            {"_id": ObjectId("609e85aa1f147c3e4ff8eaf0"),
             "order_id": "609e85aa1f147c3e4ff8eae9", "price": 100},
            {"_id": ObjectId("609e85aa1f147c3e4ff8eaf1"),
             "order_id": "609e85aa1f147c3e4ff8eae9", "price": 150}
        ]
        mock_find = MagicMock(return_value=expected_quotations)
        with patch.object(db.quotations, 'find', mock_find):
            quotations = self.repository.read_order_quotations(
                "609e85aa1f147c3e4ff8eae9")
            self.assertEqual(len(quotations), 2)
            # Additional assertions can be added to verify the content of quotations

    # Add similar test methods for other functions in the OrdersRepository class


if __name__ == '__main__':
    unittest.main()
