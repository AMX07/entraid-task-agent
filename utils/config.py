import os
import sys
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient

# Load environment variables
load_dotenv()

# Azure AD credentials
TENANT_ID = os.getenv('AZURE_TENANT_ID')
CLIENT_ID = os.getenv('AZURE_CLIENT_ID')
CLIENT_SECRET = os.getenv('AZURE_CLIENT_SECRET')

# Azure OpenAI settings
OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
OPENAI_DEPLOYMENT = os.getenv('AZURE_OPENAI_DEPLOYMENT')

# Azure Key Vault (Optional)
KEYVAULT_URL = os.getenv('AZURE_KEYVAULT_URL')

def get_credentials():
    """Get Azure credentials for authenticating with Microsoft Graph API."""
    if all([TENANT_ID, CLIENT_ID, CLIENT_SECRET]):
        return ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
    else:
        # Fall back to default credential chain
        return DefaultAzureCredential()

def get_secret_from_keyvault(secret_name):
    """Retrieve a secret from Azure Key Vault."""
    if not KEYVAULT_URL:
        return None
    
    try:
        credential = get_credentials()
        secret_client = SecretClient(vault_url=KEYVAULT_URL, credential=credential)
        return secret_client.get_secret(secret_name).value
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None

def validate_config():
    """Validate that required configuration is available."""
    required_vars = {
        'AZURE_TENANT_ID': TENANT_ID,
        'AZURE_CLIENT_ID': CLIENT_ID,
        'AZURE_CLIENT_SECRET': CLIENT_SECRET,
        'AZURE_OPENAI_ENDPOINT': OPENAI_ENDPOINT,
        'AZURE_OPENAI_API_KEY': OPENAI_API_KEY,
        'AZURE_OPENAI_DEPLOYMENT': OPENAI_DEPLOYMENT
    }
    
    missing = [key for key, value in required_vars.items() if not value]
    
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("Please check your .env file or environment variables.")
        return False
    
    return True