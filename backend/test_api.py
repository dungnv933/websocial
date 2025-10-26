#!/usr/bin/env python3
"""
Test script for SMM Panel API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get("{}/health".format(BASE_URL))
    print("Health Check:", response.status_code, response.json())

def test_register():
    """Test user registration"""
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    response = requests.post("{}/api/auth/register".format(BASE_URL), json=data)
    print("Register:", response.status_code, response.json())
    return response.json() if response.status_code == 200 else None

def test_login():
    """Test user login"""
    data = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = requests.post("{}/api/auth/login".format(BASE_URL), json=data)
    print("Login:", response.status_code, response.json())
    return response.json().get("access_token") if response.status_code == 200 else None

def test_services(token):
    """Test services endpoint"""
    headers = {"Authorization": "Bearer {}".format(token)}
    response = requests.get("{}/api/services".format(BASE_URL), headers=headers)
    print("Services:", response.status_code, response.json())

def test_user_info(token):
    """Test user info endpoint"""
    headers = {"Authorization": "Bearer {}".format(token)}
    response = requests.get("{}/api/auth/me".format(BASE_URL), headers=headers)
    print("User Info:", response.status_code, response.json())

if __name__ == "__main__":
    print("Testing SMM Panel API...")
    print("=" * 50)
    
    # Test health
    test_health()
    print()
    
    # Test registration
    user_data = test_register()
    print()
    
    # Test login
    token = test_login()
    print()
    
    if token:
        # Test authenticated endpoints
        test_user_info(token)
        print()
        test_services(token)
    
    print("=" * 50)
    print("Testing completed!")

