import pytest
import json

def test_api_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Welcome to the Flask API"}

def test_api_food_outlets(client, requests_mock, mock_uvic_index):
    requests_mock.get("https://www.uvic.ca/services/food/where/index.php", text=mock_uvic_index)
    
    response = client.get('/api/food_outlets')
    assert response.status_code == 200
    data = response.json
    
    assert "Monday - Thursday" in data
    assert "Bibliocafe" in data["Monday - Thursday"]
    assert data["Monday - Thursday"]["Bibliocafe"]["displayHours"] == "08:00 AM - 09:00 PM"

def test_api_sub_hours(client, requests_mock, mock_uvss_sub):
    requests_mock.get("https://uvss.ca/thesub/", text=mock_uvss_sub)
    
    response = client.get('/api/sub_hours')
    assert response.status_code == 200
    data = response.json
    
    assert "Monday" in data
    assert "Bean There" in data["Monday"]
    assert data["Monday"]["Bean There"]["displayHours"] == "07:30 AM - 05:30 PM"

def test_api_currently_open(client, requests_mock, mock_uvic_index):
    requests_mock.get("https://www.uvic.ca/services/food/where/index.php", text=mock_uvic_index)
    
    # Test with custom time/day: Monday at 10:00 AM
    response = client.get('/api/currently_open?time=10:00&day=monday')
    assert response.status_code == 200
    data = response.json
    
    assert data["day"] == "Monday"
    assert "Bibliocafe" in data["open_outlets"]
    assert "Mystic Market" in data["open_outlets"]

def test_api_menu_cove(client, requests_mock, mock_cove_menu):
    requests_mock.get("https://www.uvic.ca/services/food/where/thecove/index.php", text=mock_cove_menu)
    
    response = client.get('/api/menu/cove/greens')
    assert response.status_code == 200
    data = response.json
    
    assert "Salads" in data
    assert "Caesar Salad" in data["Salads"]
    assert data["Salads"]["Caesar Salad"]["dietary restrictions"] == ["vegan"]
