import json
import logging
import azure.functions as func
from app_orchestrator import EntraIDAgent

# Create the function app
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EntraIDAgentFunction')

# Initialize the agent
entra_agent = None
try:
    entra_agent = EntraIDAgent()
except Exception as e:
    logger.error(f"Failed to initialize agent: {str(e)}", exc_info=True)

@app.route(route="process_command", methods=["POST"])
def process_command(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function entry point to process natural language commands.
    
    Args:
        req: The HTTP request
        
    Returns:
        HttpResponse: Response containing results
    """
    logger.info("Processing incoming request")
    
    # Check if the agent was initialized successfully
    if not entra_agent:
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "message": "Agent not initialized. Check logs for details."
            }),
            status_code=500,
            mimetype="application/json"
        )
    
    try:
        # Get the request body
        req_body = req.get_json()
        
        # Extract the command from the request
        command = req_body.get('command')
        if not command:
            return func.HttpResponse(
                json.dumps({
                    "success": False,
                    "message": "No command provided. Please include a 'command' field in the request body."
                }),
                status_code=400,
                mimetype="application/json"
            )
            
        # Process the command
        result = entra_agent.process_command(command)
        
        # Return the result
        return func.HttpResponse(
            json.dumps(result),
            status_code=200 if result.get('success', False) else 400,
            mimetype="application/json"
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return func.HttpResponse(
            json.dumps({
                "success": False,
                "message": f"Error processing request: {str(e)}"
            }),
            status_code=500,
            mimetype="application/json"
        )