import json
import logging
from utils.config import validate_config
from utils.openai_service import OpenAIService
from utils.graph_service import GraphService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EntraIDAgent')

class EntraIDAgent:
    def __init__(self):
        """Initialize the Entra ID Agent with required services."""
        # Validate configuration before starting
        if not validate_config():
            logger.error("Configuration validation failed. Please check your environment variables.")
            raise ValueError("Invalid configuration")
            
        self.openai_service = OpenAIService()
        self.graph_service = GraphService()
        logger.info("EntraIDAgent initialized successfully")
        
    def process_command(self, command_text):
        """
        Process a natural language command and execute it.
        
        Args:
            command_text (str): The natural language command
            
        Returns:
            dict: Response containing results and status
        """
        logger.info(f"Processing command: {command_text}")
        
        try:
            # Parse the command using OpenAI
            parsed_data = self.openai_service.parse_command(command_text)
            if not parsed_data:
                return {
                    "success": False,
                    "message": "Failed to parse command. Please try rephrasing."
                }
                
            logger.info(f"Parsed command: {json.dumps(parsed_data, indent=2)}")
            
            # Execute the command based on the parsed action
            if parsed_data['action'] == 'create_app_registration':
                return self._create_app_registration(
                    parsed_data['appName'],
                    parsed_data.get('permissions', []),
                    parsed_data.get('description', '')
                )
            elif parsed_data['action'] == 'update_app_registration':
                # Implement update logic here
                return {
                    "success": False,
                    "message": "Update app registration not implemented yet"
                }
            elif parsed_data['action'] == 'delete_app_registration':
                # Implement delete logic here
                return {
                    "success": False,
                    "message": "Delete app registration not implemented yet"
                }
            else:
                return {
                    "success": False,
                    "message": f"Unknown action: {parsed_data['action']}"
                }
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error processing command: {str(e)}"
            }
            
    def _create_app_registration(self, app_name, permissions=None, description=None):
        """
        Create an app registration with the specified details.
        
        Args:
            app_name (str): The name of the application
            permissions (list, optional): List of required API permissions
            description (str, optional): Description of the application
            
        Returns:
            dict: Response containing results and status
        """
        try:
            logger.info(f"Creating app registration: {app_name}")
            
            # Create the app registration
            app = self.graph_service.create_app_registration(app_name, description)
            app_id = app['id']
            app_client_id = app['appId']
            
            logger.info(f"App registration created. ID: {app_id}, Client ID: {app_client_id}")
            
            # Create a client secret
            secret_result = self.graph_service.create_client_secret(app_id)
            client_secret = secret_result['secretText']
            secret_id = secret_result['id']
            
            logger.info(f"Client secret created. ID: {secret_id}")
            
            # Add required permissions
            if permissions:
                logger.info(f"Adding permissions: {permissions}")
                self.graph_service.add_required_permissions(app_id, permissions)
                
            # Create service principal
            logger.info("Creating service principal")
            sp = self.graph_service.create_service_principal(app_client_id)
            sp_id = sp['id']
            
            logger.info(f"Service principal created. ID: {sp_id}")
            
            # Return the results
            return {
                "success": True,
                "message": f"App registration '{app_name}' created successfully.",
                "data": {
                    "applicationId": app_client_id,
                    "objectId": app_id,
                    "servicePrincipalId": sp_id,
                    "clientSecret": client_secret
                },
                "nextSteps": [
                    "Store the client secret securely (it won't be shown again).",
                    "Admin consent may be required for application permissions."
                ]
            }
            
        except Exception as e:
            logger.error(f"Error creating app registration: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Error creating app registration: {str(e)}"
            }