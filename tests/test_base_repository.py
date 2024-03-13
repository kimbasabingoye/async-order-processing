import pytest
from unittest.mock import MagicMock
from bson import ObjectId
from pymongo import MongoClient

from src.api.database import BaseRepository, config


class TestBaseRepository:
    @pytest.fixture(scope="function")
    def test_db(self):
        # Connect to the test database
        client = MongoClient(config.mongo_url)
        db = client["test_database"]

        # Create a test collection
        db.create_collection("test_collection")

        try:
            yield db
        finally:
            # Teardown: Drop the test collection after the tests are completed
            db.drop_collection("test_collection")
            client.close()

    def test_create_and_read(self, test_db):
        # Create an instance of BaseRepository using the test database and collection
        repository = BaseRepository(test_db, "test_collection")

        # Define the document to be inserted
        document_to_insert = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.com"
        }

        # Insert the document
        inserted_id = repository.create(document_to_insert)
        # print(f"inserted_id {inserted_id}")

        # Retrieve the inserted document from the database
        inserted_document = repository.read(ObjectId(inserted_id))
        # print(f"Inserted doc: {inserted_document}")

        # Assert that the inserted document matches the original document
        assert inserted_document["id"] == inserted_id
        assert inserted_document["first_name"] == "Alice"
        assert inserted_document["last_name"] == "Smith"
        assert inserted_document["email"] == "alice.smith@example.com"

    def test_read_all(self, test_db):
        repository = BaseRepository(test_db, "test_collection")

        # Test data
        test_data = [
            {"first_name": "Alice", "last_name": "Smith",
                "email": "alice.smith@example.com"},
            {"first_name": "Bob", "last_name": "Jones",
                "email": "bob.jones@example.com"}
        ]

        # Insert test data into the collection
        for data in test_data:
            repository.create(data)

        # Read all objects from the collection
        all_objects = repository.read_all()

        # Assert that the number of retrieved objects matches the number of inserted test data
        assert len(all_objects) == len(test_data)
    
    def test_check_exists_and_delete(self, test_db):
        # Create an instance of BaseRepository using the test database and collection
        repository = BaseRepository(test_db, "test_collection")

        # Define the document to be inserted
        document_to_insert = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@example.com"
        }

        # Insert the document
        inserted_id = repository.create(document_to_insert)

        # Check if the inserted document exists
        assert repository.check_exists(inserted_id)

        # Delete the document
        delete_result = repository.delete(inserted_id)
        assert delete_result is True

        # Check that the document no longer exists
        assert not repository.check_exists(inserted_id)
