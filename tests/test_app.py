"""
Unit tests for the Flask application (`app.py`).

This file contains test to validate the functionality of the `/process` endpoint,
ensuring correct behavior for valid inputs, missing fields, and authentication errors.
"""
import base64
import json

import pytest

from app import app
from flask import jsonify


@pytest.fixture
def client():
    """
    Fixture to set up the test client for the Flask app.

    Returns:
        flask.testing.FlaskClient: A test client for sending HTTP requests to the application.
    """
    app.config['TESTING'] = True
    return app.test_client()

@pytest.fixture
def valid_auth_headers():
    """
    Fixture for valid authorization headers.

    Returns:
        dict: A dictionary containing valid HTTP Basic Auth headers.
    """
    username = "heroku"
    password = "agent"
    encoded_credentials = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
    return {"Authorization": f"Basic {encoded_credentials}"}

@pytest.fixture
def invalid_auth_headers():
    """
    Fixture for invalid authentication headers.

    Returns:
        dict: A dictionary containing invalid HTTP Basic Auth headers.
    """
    username = "invalid"
    password = "wrong"
    encoded_credentials = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
    return {"Authorization": f"Basic {encoded_credentials}"}

def test_process_endpoint_success(client, valid_auth_headers):
    """
    Test the `/process` endpoint with valid credentials and input.

    Verifies that the endpoint returns a 200 status code and a Base64-encoded badge
    in the response.
    """
    payload = {"name": "Neo"}
    response = client.post("/process",
                           data=json.dumps(payload),
                           headers=valid_auth_headers,
                           content_type="application/json"
                           )

    assert response.status_code == 200, f"Unexpected status code: {response.status_code}"
    assert "message" in response.json, "Response should contain a message field"
    assert '<img src="data:image/png;base64' in response.json["message"], \
        "Response message does not contain a Base64 badge"

def test_process_endpoint_missing_name(client, valid_auth_headers):
    """
    Test the `/process` endpoint with missing 'name' field.

    Verifies that the endpoint returns a 400 status code and an appropriate error message.
    """
    payload = {}

    response = client.post("/process",
                           data=json.dumps(payload),
                           headers=valid_auth_headers,
                           content_type="application/json"
                           )

    print("Raw response body: ", response.data.decode())
    print("Content-Type header: ", response.headers.get("Content-Type"))

    assert response.status_code == 400, f"Unexpected status code: {response.status_code}"
    try:
        response_data = response.get_json()
        assert response_data is not None, "Response is not JSON"
        assert response_data.get("error") == "Invalid request, 'name' field is required", \
            f"Unexpected error message: {response_data}"
    except Exception as e:
        print("Response could not be parsed as JSON: ", response.data.decode())
        raise AssertionError("Failed to parse JSON response") from e

def test_process_endpoint_invalid_auth(client, invalid_auth_headers):
    """
    Test the '/process' endpoint with invalid credentials.
    
    Verifies that the endpoint returns a 401 status code and an unauthorized access error.
    """
    payload = {"name": "Neo"}
    response = client.post("/process",
                           data=json.dumps(payload),
                           headers=invalid_auth_headers,
                           content_type="application/json"
                           )

    assert response.status_code == 401, f"Unexpected status code: {response.status_code}"
    assert "Unauthorized" in response.data.decode(), "Expected unauthorized access error"