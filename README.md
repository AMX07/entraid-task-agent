# Entra ID Task Agent

A Python-based AI agent for Microsoft Entra ID (formerly Azure AD) tasks using natural language commands. This agent uses Azure OpenAI to parse natural language commands and the Microsoft Graph API to perform operations.

## Features

- Process natural language commands related to Entra ID operations
- Create app registrations with specified permissions and descriptions
- Generate and manage client secrets
- Secure integration with Azure Key Vault (optional)
- Available as an Azure Function or local Flask server

## Architecture

The agent consists of the following components:

- **Natural Language Parser**: Uses Azure OpenAI to interpret commands and extract structured data.
- **Microsoft Graph API Client**: Handles interactions with Entra ID via the Graph API.
- **Orchestrator**: Coordinates the flow between command parsing and API calls.
- **API Endpoints**: Provides HTTP endpoints for integration with other systems.

## Prerequisites

- Python 3.8 or higher
- Azure subscription
- Azure OpenAI deployment with a model (e.g., GPT-3.5)
- Entra ID admin permissions
- Azure Functions Core Tools (for deployment)

## Setup

1. Clone this repository:
```bash
git clone https://github.com/yourusername/entraid-agent.git
cd entraid-agent
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Create a `.env` file with your credentials (see `.env.example` for template):
```
# Copy from .env.example and fill in your values
cp .env.example .env
```

4. Run the local server:
```bash
python local_server.py
```

## Usage

Send a POST request to the API endpoint with your natural language command:

```bash
curl -X POST http://localhost:5000/api/process-command \
  -H "Content-Type: application/json" \
  -d '{"command": "Create an app registration named REACH SharePoint Integration that needs Sites.Read.All permissions to read SharePoint lists for progress graphs"}'
```

Example response:

```json
{
  "success": true,
  "message": "App registration 'REACH SharePoint Integration' created successfully.",
  "data": {
    "applicationId": "11111111-1111-1111-1111-111111111111",
    "objectId": "22222222-2222-2222-2222-222222222222",
    "servicePrincipalId": "33333333-3333-3333-3333-333333333333",
    "clientSecret": "JkLmN~.PqRs.TuVwX~yZaBcDeFgHiJ"
  },
  "nextSteps": [
    "Store the client secret securely (it won't be shown again).",
    "Admin consent may be required for application permissions."
  ]
}
```

## Deployment to Azure Functions

1. Deploy the function app to Azure:
```bash
func azure functionapp publish your-function-app-name
```

2. Set up the environment variables in the Azure Function app settings.

## Security Considerations

- Store client secrets securely in Azure Key Vault
- Use managed identities for authentication where possible
- Enable monitoring and logging for security auditing
- Implement proper access controls for the API endpoints

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.