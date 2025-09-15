import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os
from bson import ObjectId

# Add the api directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_read_root(self, client):
        """Test GET / endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}


class TestAgeGroupEndpoints:
    """Test age group related endpoints"""
    
    def test_create_age_group(self, client):
        """Test POST /age-groups endpoint"""
        age_group_data = {
            "min_age": 25,
            "max_age": 35,
            "description": "Young Adult"
        }
        
        response = client.post("/age-groups", json=age_group_data)
        assert response.status_code == 200
        assert response.json() == age_group_data
    
    def test_list_age_groups(self, client):
        """Test GET /age-groups endpoint"""
        response = client.get("/age-groups")
        assert response.status_code == 200
        data = response.json()
        assert "age_groups" in data
        assert isinstance(data["age_groups"], list)
    
    def test_update_age_group_success(self, client):
        """Test PUT /age-groups/{age_group_id} endpoint with valid ID"""
        valid_id = str(ObjectId())
        updated_data = {
            "min_age": 41,
            "max_age": 51,
            "description": "Updated Middle Age"
        }
        
        response = client.put(f"/age-groups/{valid_id}", json=updated_data)
        assert response.status_code == 200
        response_data = response.json()
        assert "modified_count" in response_data
        assert "matched_count" in response_data
    
    def test_delete_age_group_success(self, client):
        """Test DELETE /age-groups/{age_group_id} endpoint with valid ID"""
        valid_id = str(ObjectId())
        
        response = client.delete(f"/age-groups/{valid_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Age group deleted successfully"}
    
    def test_update_age_group_invalid_id(self, client):
        """Test PUT /age-groups/{age_group_id} with invalid ID format"""
        invalid_id = "invalid_id"
        age_group_data = {
            "min_age": 30,
            "max_age": 40,
            "description": "Test"
        }
        
        response = client.put(f"/age-groups/{invalid_id}", json=age_group_data)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, tuple)
        assert "error" in response_data[0]
        assert "Invalid ID format" in response_data[0]["error"]
    
    def test_delete_age_group_invalid_id(self, client):
        """Test DELETE /age-groups/{age_group_id} with invalid ID format"""
        invalid_id = "invalid_id"
        
        response = client.delete(f"/age-groups/{invalid_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, tuple)
        assert "error" in response_data[0]
        assert "Invalid ID format" in response_data[0]["error"]


class TestEnrollEndpoints:
    """Test enroll related endpoints"""
    
    def test_create_enroll_success(self, client):
        """Test POST /enroll endpoint with valid data"""
        enroll_data = {
            "name": "João Silva",
            "cpf": "123.456.789-00",
            "age": 25
        }
        
        response = client.post("/enroll", json=enroll_data)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], str)
    
    def test_create_enroll_no_age_group(self, client):
        """Test POST /enroll endpoint with age that doesn't match any age group"""
        # Mock the age group collection to return None (no matching age group)
        with patch('run.ageGroupCollection') as mock_collection:
            mock_collection.find_one.return_value = None
            
            enroll_data = {
                "name": "Maria Santos",
                "cpf": "987.654.321-00",
                "age": 150  # Age that won't match any age group
            }
            
            response = client.post("/enroll", json=enroll_data)
            assert response.status_code == 400
            assert "No age group found for this age" in response.json()["detail"]
    
    def test_list_enrolls(self, client):
        """Test GET /enroll endpoint"""
        response = client.get("/enroll")
        assert response.status_code == 200
        data = response.json()
        assert "enrolls" in data
        assert isinstance(data["enrolls"], list)
    
    def test_get_enroll_success(self, client):
        """Test GET /enroll/{enroll_id} endpoint with valid ID"""
        # Mock the collection to return a sample enroll
        sample_enroll = {
            "_id": ObjectId(),
            "name": "Pedro Costa",
            "cpf": "111.222.333-44",
            "age": 30,
            "status": "pending",
            "age_group": {
                "min_age": 18,
                "max_age": 59,
                "description": "Adult"
            }
        }
        
        with patch('run.enrollCollection') as mock_collection:
            mock_collection.find_one.return_value = sample_enroll
            
            valid_id = str(sample_enroll["_id"])
            response = client.get(f"/enroll/{valid_id}")
            assert response.status_code == 200
            data = response.json()
            assert "enroll" in data
    
    def test_get_enroll_not_found(self, client):
        """Test GET /enroll/{enroll_id} with nonexistent ID"""
        with patch('run.enrollCollection') as mock_collection:
            mock_collection.find_one.return_value = None
            
            fake_id = str(ObjectId())
            response = client.get(f"/enroll/{fake_id}")
            assert response.status_code == 200
            response_data = response.json()
            assert isinstance(response_data, tuple)
            assert "error" in response_data[0]
            assert "Enroll not found" in response_data[0]["error"]
    
    def test_get_enroll_invalid_id(self, client):
        """Test GET /enroll/{enroll_id} with invalid ID format"""
        invalid_id = "invalid_id"
        response = client.get(f"/enroll/{invalid_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, tuple)
        assert "error" in response_data[0]
        assert "Invalid ID format" in response_data[0]["error"]
    
    def test_update_enroll_success(self, client):
        """Test PUT /enroll/{enroll_id} endpoint with valid data"""
        valid_id = str(ObjectId())
        update_data = {
            "name": "Ana Lima Santos",
            "age": 29
        }
        
        response = client.put(f"/enroll/{valid_id}", json=update_data)
        assert response.status_code == 200
        response_data = response.json()
        assert "modified_count" in response_data
        assert "matched_count" in response_data
    
    def test_update_enroll_invalid_id(self, client):
        """Test PUT /enroll/{enroll_id} with invalid ID format"""
        invalid_id = "invalid_id"
        update_data = {
            "name": "Test Name"
        }
        
        response = client.put(f"/enroll/{invalid_id}", json=update_data)
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, tuple)
        assert "error" in response_data[0]
        assert "Invalid ID format" in response_data[0]["error"]
    
    def test_delete_enroll_success(self, client):
        """Test DELETE /enroll/{enroll_id} endpoint with valid ID"""
        valid_id = str(ObjectId())
        
        response = client.delete(f"/enroll/{valid_id}")
        assert response.status_code == 200
        assert response.json() == {"message": "Enroll deleted successfully"}
    
    def test_delete_enroll_not_found(self, client):
        """Test DELETE /enroll/{enroll_id} with nonexistent ID"""
        with patch('run.enrollCollection') as mock_collection:
            mock_collection.delete_one.return_value.deleted_count = 0
            
            fake_id = str(ObjectId())
            response = client.delete(f"/enroll/{fake_id}")
            assert response.status_code == 200
            response_data = response.json()
            assert isinstance(response_data, tuple)
            assert "error" in response_data[0]
            assert "Enroll not found" in response_data[0]["error"]
    
    def test_delete_enroll_invalid_id(self, client):
        """Test DELETE /enroll/{enroll_id} with invalid ID format"""
        invalid_id = "invalid_id"
        response = client.delete(f"/enroll/{invalid_id}")
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, tuple)
        assert "error" in response_data[0]
        assert "Invalid ID format" in response_data[0]["error"]


class TestDataValidation:
    """Test data validation for API endpoints"""
    
    def test_create_enroll_missing_fields(self, client):
        """Test POST /enroll with missing required fields"""
        incomplete_data = {
            "name": "Test User"
            # Missing cpf and age
        }
        
        response = client.post("/enroll", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_enroll_invalid_age_type(self, client):
        """Test POST /enroll with invalid age type"""
        invalid_data = {
            "name": "Test User",
            "cpf": "123.456.789-00",
            "age": "invalid_age"  # Should be int
        }
        
        response = client.post("/enroll", json=invalid_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_age_group_missing_fields(self, client):
        """Test POST /age-groups with missing required fields"""
        incomplete_data = {
            "min_age": 20
            # Missing max_age and description
        }
        
        response = client.post("/age-groups", json=incomplete_data)
        assert response.status_code == 422  # Validation error
    
    def test_create_age_group_invalid_age_types(self, client):
        """Test POST /age-groups with invalid age types"""
        invalid_data = {
            "min_age": "invalid",
            "max_age": "invalid",
            "description": "Test Group"
        }
        
        response = client.post("/age-groups", json=invalid_data)
        assert response.status_code == 422  # Validation error
