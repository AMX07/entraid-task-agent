import json
import openai
from . import config

class OpenAIService:
    def __init__(self):
        """Initialize the OpenAI service with Azure OpenAI configurations."""
        openai.api_type = "azure"
        openai.api_base = config.OPENAI_ENDPOINT
        openai.api_key = config.OPENAI_API_KEY
        openai.api_version = "2023-05-15"  # Update this to the version you're using
        self.deployment_name = config.OPENAI_DEPLOYMENT

    def parse_command(self, command_text):
        """
        Parse a natural language command into structured data using Azure OpenAI.
        
        Args:
            command_text (str): The natural language command
            
        Returns:
            dict: Structured data extracted from the command
        """
        try:
            # Create a system message that instructs the model how to parse commands
            system_prompt = """
            You are an AI assistant specialized in parsing natural language commands related to Microsoft Entra ID (formerly Azure AD) operations.
            Your task is to extract structured information from the user's command.
            
            For app registration commands, extract the following information:
            - action: The specific action (e.g., create_app_registration, update_app_registration, delete_app_registration)
            - appName: The name of the app registration
            - permissions: List of required API permissions (e.g., ["Sites.Read.All", "User.Read"])
            - description: Purpose of the app registration
            
            Return the extracted information as valid JSON with these fields only when relevant.
            If you cannot confidently extract a piece of information, leave that field empty.
            """

            response = openai.ChatCompletion.create(
                engine=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": command_text}
                ],
                temperature=0.0,  # Use low temperature for deterministic results
                max_tokens=800,
                n=1,
                stop=None
            )
            
            parsed_response = response.choices[0].message.content.strip()
            
            # Try to extract valid JSON from the response
            try:
                # Find JSON in the response if it's wrapped in text or code blocks
                json_start = parsed_response.find('{')
                json_end = parsed_response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = parsed_response[json_start:json_end]
                    parsed_data = json.loads(json_str)
                else:
                    # Try parsing the whole response as JSON
                    parsed_data = json.loads(parsed_response)
                
                # Validate the parsed data
                if self._validate_parsed_data(parsed_data):
                    return parsed_data
                else:
                    raise ValueError("Parsed data is missing required fields")
                    
            except json.JSONDecodeError:
                raise ValueError(f"Failed to decode JSON from response: {parsed_response}")
                
        except Exception as e:
            print(f"Error parsing command: {e}")
            return None
    
    def _validate_parsed_data(self, data):
        """
        Validate that the parsed data contains the necessary fields based on the action.
        
        Args:
            data (dict): The parsed data to validate
            
        Returns:
            bool: True if the data is valid, False otherwise
        """
        if not isinstance(data, dict):
            return False
            
        if 'action' not in data:
            return False
            
        # Different actions require different fields
        if data['action'] == 'create_app_registration':
            required_fields = ['appName']
            if not all(field in data for field in required_fields):
                return False
                
        return True