import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
from bson import ObjectId

# Add the api directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

@pytest.fixture
def client():
    """Create test client with mocked MongoDB"""
    with patch('pymongo.MongoClient') as mock_client:
        # Mock the MongoDB client and collections
        mock_db = MagicMock()
        mock_client.return_value.__getitem__.return_value = mock_db
        
        # Setup mock collections
        mock_enroll_collection = MagicMock()
        mock_age_group_collection = MagicMock()
        mock_message_collection = MagicMock()
        
        mock_db.__getitem__.side_effect = lambda key: {
            'enrollCollection': mock_enroll_collection,
            'ageGroupCollection': mock_age_group_collection,
            'messageCollection': mock_message_collection
        }[key]
        
        # Setup default age group data for tests
        sample_age_group = {
            "_id": ObjectId(),
            "min_age": 18,
            "max_age": 59,
            "description": "Adult"
        }
        mock_age_group_collection.find_one.return_value = sample_age_group
        mock_age_group_collection.find.return_value = [sample_age_group]
        
        # Setup default responses
        mock_enroll_collection.insert_one.return_value.inserted_id = ObjectId()
        mock_message_collection.insert_one.return_value.inserted_id = ObjectId()
        mock_enroll_collection.find.return_value = []
        mock_enroll_collection.find_one.return_value = None
        mock_enroll_collection.update_one.return_value.modified_count = 1
        mock_enroll_collection.update_one.return_value.matched_count = 1
        mock_enroll_collection.delete_one.return_value.deleted_count = 1
        
        mock_age_group_collection.insert_one.return_value.inserted_id = ObjectId()
        mock_age_group_collection.update_one.return_value.modified_count = 1
        mock_age_group_collection.update_one.return_value.matched_count = 1
        mock_age_group_collection.delete_one.return_value.deleted_count = 1
        
        from run import app
        with TestClient(app) as test_client:
            yield test_client
