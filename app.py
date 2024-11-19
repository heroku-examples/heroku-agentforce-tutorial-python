import os
import logging
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_httpauth import HTTPBasicAuth
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
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRequest:
    def __init__(self, name):
        self.name = name

class AgentResponse:
    def __init__(self, message):
        self.message = message
    def to_dict(self):
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
    @auth.login_required  # Protect the endpoint with HTTP Basic Auth
    @api.expect(agent_request_model)  # Use the model here    
    @api.response(200, 'Success', agent_response_model)  # Define the response model here
    def post(self):
        # Parse the JSON data from the request body
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Invalid request, 'name' field is required"}), 400

        # Create MyRequest instance from JSON data
        agentRequest = AgentRequest(data['name'])
        logger.info("Received query: %s", agentRequest.name)
        
        # Create badge and embed in HTML
        try:
            base64_image = create_badge("Heroku Agent Action", f"Deployed by {agentRequest.name}")
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

        agentResponse = AgentResponse(message)
        logger.info("Result is: %s", agentResponse)
        return agentResponse.to_dict()

if __name__ == '__main__':
    # Use the PORT environment variable if present, otherwise default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
