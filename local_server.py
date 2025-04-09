import json
import logging
from flask import Flask, request, jsonify
from app_orchestrator import EntraIDAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EntraIDLocalServer')

# Create Flask app
app = Flask(__name__)

# Initialize the agent
entra_agent = None
try:
    entra_agent = EntraIDAgent()
except Exception as e:
    logger.error(f"Failed to initialize agent: {str(e)}", exc_info=True)

@app.route('/api/process-command', methods=['POST'])
def process_command():
    """
    Flask endpoint to process natural language commands.
    
    Returns:
        Response: JSON response containing results
    """
    logger.info("Processing incoming request")
    
    # Check if the agent was initialized successfully
    if not entra_agent:
        return jsonify({
            "success": False,
            "message": "Agent not initialized. Check logs for details."
        }), 500
    
    try:
        # Get the request body
        req_body = request.json
        
        # Extract the command from the request
        command = req_body.get('command')
        if not command:
            return jsonify({
                "success": False,
                "message": "No command provided. Please include a 'command' field in the request body."
            }), 400
            
        # Process the command
        result = entra_agent.process_command(command)
        
        # Return the result
        return jsonify(result), 200 if result.get('success', False) else 400
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error processing request: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Display startup message
    if entra_agent:
        logger.info("EntraID Agent started successfully")
        print("\n✅ EntraID Agent started successfully")
        print("📡 API endpoint available at: http://localhost:5000/api/process-command")
        print("💡 Usage: Send POST requests with JSON body: {\"command\": \"your natural language command here\"}")
    else:
        logger.error("EntraID Agent failed to start. Check logs for details.")
        print("\n❌ EntraID Agent failed to start. Check logs for details.")
    
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)