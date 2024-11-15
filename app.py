import logging

from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app,
          title='Agentforce Action',
          description="Basic Agentforce Action example",
          version='0.1.0'
          )

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
        message='A response to the agent'
    )
})

### API Routes
@api.route('/process')
class Process(Resource):
    @api.expect(agent_request_model)  # Use the model here    
    @api.response(200, 'Success', agent_response_model)  # Define the response model here
    def post(self):
        """
        This is an API endpoint for the Agent Action
        """
        # Parse the JSON data from the request body
        data = request.json
        if not data or 'name' not in data:
            return jsonify({"error": "Invalid request, 'name' field is required"}), 400

        # Create MyRequest instance from JSON data
        agentRequest = AgentRequest(data['name'])
        logger.info("Received query: %s", agentRequest.name)
        
        # Create AgentResponse instance
        message = "Welcome " + agentRequest.name + " to the Matrix"
        agentResponse = AgentResponse(message)
        logger.info("Result is: %s", agentResponse)
        return agentResponse.to_dict()

if __name__ == '__main__':
    app.run(debug=True)
