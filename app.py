"""
Agentforce Action API

This module implements a simple Flask-based API for handling agent requests and generating dynamic badges.
The API provides a single endpoint (`/process`) that accepts a JSON payload containing a name,
generates a badge with the provided name, and returns an HTML fragment of the badge.

Key Features:
- Implements HTTP Basic Authentication to protect the `/process` endpoint.
- Utilizes Flask-RESTx for API documentation and validation.
- Generates a badge using an external `badgecreator` module and returns it as part of the response.
- Logs incoming requests and badge generation activity for debugging purposes.

Classes:
    AgentRequest: Represents an agent request containing a name.
    AgentResponse: Represents a response to the agent with a message.

Endpoints:
    POST /process:
        - Input: JSON payload containing a `name` field.
        - Output: HTML fragment with a base64-encoded badge or an error message.

Usage:
    - Run the application with `python <filename>.py`.
    - The server listens on the port specified in the `PORT` environment variable or defaults to 5000.
    - Use an HTTP client (e.g., Postman, curl) to interact with the `/process` endpoint.

Dependencies:
    - Flask
    - Flask-RESTx
    - Flask-HTTPAuth
    - Werkzeug (for password hashing)
    - badgecreator (external module for badge generation)
"""
import logging
import os

from flask import Flask, jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_restx import Api, Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash

from badgecreator import create_badge

app = Flask(__name__)
api = Api(app,
          title='Agentforce Action',
          description="Basic Agentforce Action example",
          version='0.1.0'
          )

auth = HTTPBasicAuth()

# Define a hardcoded user with a hashed password
users = {
    "heroku": generate_password_hash("agent")
}

# Verify the username and password
@auth.verify_password
def verify_password(username, password):
    """
    Verifies a user's credentials using HTTP Basic Auth.

    Parameters:
        username (str): The provided username.
        password (str): The provided password.

    Returns:
        str: The username if the authentication succeeds, otherwise None.
    """
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRequest:
    """
    Represents an agent request containing a name.

    Attributes:
        name (str): The name included in the request.
    """
    def __init__(self, name):
        self.name = name

class AgentResponse:
    """
    Represents a response to an agent request.

    Attributes:
        message (str): The response message.
    """
    def __init__(self, message):
        self.message = message

    def to_dict(self):
        """
        Converts the agent_response object to a dictionary.

        Returns:
            dict: A dictionary representation of the agent_response.
        """
        return {"message": self.message}

# Define the AgentRequest model for the input
agent_request_model = api.model('AgentRequest', {
    'name': fields.String(
        required=True,
        description='A name from the agent request',
        default="Neo"  # Default value for the OpenAPI schema
    )
})

# Define the AgentResponse model for the output
agent_response_model = api.model('AgentResponse', {
    'message': fields.String(
        required=True,
        description='A response to the agent'
    )
})

# API Routes
@api.route('/process')
class Process(Resource):
    """
    RESTful resource for processing agent requests and returning a response.
    """

    @auth.login_required  # Protect the endpoint with HTTP Basic Auth
    @api.expect(agent_request_model)  # Use the model here    
    @api.response(200, 'Success', agent_response_model)  # Define the response model here
    def post(self):
        """
        Handles POST requests to process an agent request.

        Parses input data, generates a badge with the provided name, and returns
        an HTML fragment of the badge or an error message if the badge creation fails.

        Returns:
            dict: A dictionary containing the response to the agent.
        """
        # Parse the JSON data from the request body
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Invalid request, 'name' field is required"}), 400

        # Create MyRequest instance from JSON data
        agent_request = AgentRequest(data['name'])
        logger.info("Received query: %s", agent_request.name)
        
        # Create badge and embed in HTML
        try:
            base64_image = create_badge("Heroku Agent Action", f"Deployed by {agent_request.name}")
            html_fragment = f'<img src="data:image/png;base64,{base64_image}">'
            message = html_fragment

            # Save debug.html with the generated image
            debug_html = f"<body style='background: black'>{html_fragment}</body>"
            with open("debug.html", "w") as debug_file:
                debug_file.write(debug_html)
                logger.info("Saved debug.html")
        except Exception as e:
            logger.error("Error generating badge: %s", str(e))
            message = "Error generating badge"

        agent_response = AgentResponse(message)
        logger.info("Result is: %s", agent_response)
        return agent_response.to_dict()

if __name__ == '__main__':
    """
    Entry point for the application. Starts the Flask server and runs the application.
    """
    # Use the PORT environment variable if present, otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
