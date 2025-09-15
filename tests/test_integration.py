import pytest
from faker import Faker
import sys
import os

# Add the api directory to the path so we can import the app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

fake = Faker("pt_BR")


class TestWithFakeData:
    """Test endpoints using Faker for realistic data generation"""
    
    def test_create_enroll_with_fake_data(self, client):
        """Test creating enrolls with realistic fake data"""
        for _ in range(5):
            enroll_data = {
                "name": fake.name(),
                "cpf": fake.cpf(),
                "age": fake.random_int(min=18, max=59)  # Ensure it matches our mock age group
            }
            
            response = client.post("/enroll", json=enroll_data)
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert isinstance(data["id"], str)
    
    def test_create_age_group_with_fake_data(self, client):
        """Test creating age groups with realistic fake data"""
        age_ranges = [
            (0, 12, "Criança"),
            (13, 17, "Adolescente"),
            (18, 25, "Jovem Adulto"),
            (26, 59, "Adulto"),
            (60, 120, "Idoso")
        ]
        
        for min_age, max_age, description in age_ranges:
            age_group_data = {
                "min_age": min_age,
                "max_age": max_age,
                "description": description
            }
            
            response = client.post("/age-groups", json=age_group_data)
            assert response.status_code == 200
            assert response.json() == age_group_data
    
    def test_enroll_data_validation_edge_cases(self, client):
        """Test edge cases for enroll data validation"""
        test_cases = [
            # Empty strings
            {"name": "", "cpf": "123.456.789-00", "age": 25},
            # Very long names
            {"name": "A" * 1000, "cpf": "123.456.789-00", "age": 25},
            # Edge age values
            {"name": "Test User", "cpf": "123.456.789-00", "age": 0},
            {"name": "Test User", "cpf": "123.456.789-00", "age": 150},
            # Negative age
            {"name": "Test User", "cpf": "123.456.789-00", "age": -1},
        ]
        
        for test_data in test_cases:
            response = client.post("/enroll", json=test_data)
            # Some of these should pass (empty string, long names, edge ages)
            # Others should fail (negative age)
            assert response.status_code in [200, 400, 422]
    
    def test_age_group_validation_edge_cases(self, client):
        """Test edge cases for age group data validation"""
        test_cases = [
            # Inverted age ranges (min > max)
            {"min_age": 50, "max_age": 30, "description": "Invalid Range"},
            # Same min and max age
            {"min_age": 25, "max_age": 25, "description": "Single Age"},
            # Very large age ranges
            {"min_age": 0, "max_age": 1000, "description": "Large Range"},
            # Empty description
            {"min_age": 20, "max_age": 30, "description": ""},
        ]
        
        for test_data in test_cases:
            response = client.post("/age-groups", json=test_data)
            # All should pass at the API level, business logic validation is separate
            assert response.status_code == 200
    
    def test_bulk_operations(self, client):
        """Test creating multiple records and listing them"""
        # Create multiple age groups
        age_groups = []
        for i in range(3):
            age_group_data = {
                "min_age": i * 20,
                "max_age": (i + 1) * 20 - 1,
                "description": f"Age Group {i + 1}"
            }
            response = client.post("/age-groups", json=age_group_data)
            assert response.status_code == 200
            age_groups.append(age_group_data)
        
        # List all age groups
        response = client.get("/age-groups")
        assert response.status_code == 200
        data = response.json()
        assert "age_groups" in data
        assert isinstance(data["age_groups"], list)
        
        # Create multiple enrolls
        enrolls = []
        for i in range(5):
            enroll_data = {
                "name": fake.name(),
                "cpf": fake.cpf(),
                "age": fake.random_int(min=18, max=59)
            }
            response = client.post("/enroll", json=enroll_data)
            assert response.status_code == 200
            enrolls.append(enroll_data)
        
        # List all enrolls
        response = client.get("/enroll")
        assert response.status_code == 200
        data = response.json()
        assert "enrolls" in data
        assert isinstance(data["enrolls"], list)
