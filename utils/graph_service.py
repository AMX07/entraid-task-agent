import requests
import json
import uuid
from datetime import datetime, timedelta
import time
from . import config

class GraphService:
    def __init__(self):
        """Initialize the Microsoft Graph service with authentication."""
        self.credential = config.get_credentials()
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.token = None
        self.token_expires = None
    
    def _get_token(self):
        """Get an access token for Microsoft Graph API."""
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token
            
        # Get token for Microsoft Graph
        token_response = self.credential.get_token("https://graph.microsoft.com/.default")
        self.token = token_response.token
        # Set token expiry (subtract 5 minutes for safety margin)
        self.token_expires = datetime.now() + timedelta(seconds=token_response.expires_on - 300)
        
        return self.token
        
    def _make_request(self, method, endpoint, data=None, params=None):
        """
        Make a request to the Microsoft Graph API.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint (without base URL)
            data (dict, optional): Request body
            params (dict, optional): Query parameters
            
        Returns:
            dict: API response
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self._get_token()}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params
            )
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
                
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making Graph API request: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            raise
    
    def create_app_registration(self, app_name, description=None):
        """
        Create a new app registration in Entra ID.
        
        Args:
            app_name (str): The name of the application
            description (str, optional): Description of the application
            
        Returns:
            dict: The created application
        """
        app_data = {
            "displayName": app_name,
            "signInAudience": "AzureADMyOrg",  # Single tenant
            "web": {
                "redirectUris": [
                    "https://localhost:44321"  # Default redirect URI for testing
                ],
                "implicitGrantSettings": {
                    "enableIdTokenIssuance": True
                }
            }
        }
        
        if description:
            app_data["notes"] = description
            
        return self._make_request("POST", "/applications", data=app_data)
        
    def create_client_secret(self, app_id, display_name="Default Secret"):
        """
        Create a client secret for an application.
        
        Args:
            app_id (str): The application ID
            display_name (str): Display name for the secret
            
        Returns:
            dict: The created secret information (including value which needs to be saved)
        """
        secret_data = {
            "passwordCredential": {
                "displayName": display_name,
                # Secret valid for 1 year (can be adjusted based on security needs)
                "endDateTime": (datetime.now() + timedelta(days=365)).isoformat()
            }
        }
        
        return self._make_request(
            "POST", 
            f"/applications/{app_id}/addPassword",
            data=secret_data
        )
    
    def add_required_permissions(self, app_id, permissions):
        """
        Add required resource permissions to an app registration.
        
        Args:
            app_id (str): The application ID
            permissions (list): List of permission strings (e.g., ["Sites.Read.All"])
            
        Returns:
            bool: True if successful
        """
        if not permissions:
            return True
            
        # First get the current permissions
        app = self._make_request("GET", f"/applications/{app_id}")
        
        # Map of common Microsoft APIs to their IDs
        api_map = {
            "Microsoft Graph": "00000003-0000-0000-c000-000000000000",
            "SharePoint": "00000003-0000-0ff1-ce00-000000000000",
            "Exchange": "00000002-0000-0ff1-ce00-000000000000"
        }
        
        # For each permission, add it to the requiredResourceAccess field
        # Here we're assuming most permissions are for Microsoft Graph
        graph_api_id = api_map["Microsoft Graph"]
        
        # Get the service principal to find permission IDs
        # Note: In a production app, you might want to cache this
        graph_permissions = self._make_request(
            "GET", 
            f"/servicePrincipals?$filter=appId eq '{graph_api_id}'&$select=appRoles,oauth2PermissionScopes"
        )["value"][0]
        
        # Build the requiredResourceAccess object
        required_access = app.get("requiredResourceAccess", [])
        graph_access = next(
            (ra for ra in required_access if ra["resourceAppId"] == graph_api_id), 
            {"resourceAppId": graph_api_id, "resourceAccess": []}
        )
        
        if graph_access not in required_access:
            required_access.append(graph_access)
        
        # For each permission, find its ID and add it to the access object
        for permission in permissions:
            # Determine if this is a delegated or application permission
            # Application permissions are in appRoles
            # Delegated permissions are in oauth2PermissionScopes
            permission_type = "Application"  # Default to Application permission
            if "." in permission:
                scope_parts = permission.split(".")
                if scope_parts[-1] == "All":
                    permission_type = "Application"
                else:
                    permission_type = "Delegated"
            
            # Find the permission ID
            if permission_type == "Application":
                permission_def = next(
                    (p for p in graph_permissions.get("appRoles", []) if p["value"] == permission),
                    None
                )
            else:
                permission_def = next(
                    (p for p in graph_permissions.get("oauth2PermissionScopes", []) if p["value"] == permission),
                    None
                )
                
            if not permission_def:
                print(f"Warning: Permission {permission} not found")
                continue
                
            # Add the permission if it's not already there
            permission_id = permission_def["id"]
            permission_type_value = "Role" if permission_type == "Application" else "Scope"
            
            # Check if the permission is already in the list
            if not any(ra["id"] == permission_id for ra in graph_access["resourceAccess"]):
                graph_access["resourceAccess"].append({
                    "id": permission_id,
                    "type": permission_type_value
                })
                
        # Update the application with the new permissions
        update_data = {
            "requiredResourceAccess": required_access
        }
        
        self._make_request("PATCH", f"/applications/{app_id}", data=update_data)
        return True
        
    def create_service_principal(self, app_id):
        """
        Create a service principal for an application.
        
        Args:
            app_id (str): The application ID
            
        Returns:
            dict: The created service principal
        """
        sp_data = {
            "appId": app_id
        }
        
        return self._make_request("POST", "/servicePrincipals", data=sp_data)
        
    def grant_admin_consent(self, service_principal_id, permission_ids):
        """
        Grant admin consent for permissions (requires admin privileges).
        
        Args:
            service_principal_id (str): The service principal ID
            permission_ids (list): List of permission IDs to grant
            
        Returns:
            bool: True if successful
        """
        for permission_id in permission_ids:
            consent_data = {
                "clientAppId": service_principal_id,
                "consentType": "AllPrincipals",
                "resourceId": permission_id,
                "scope": permission_id
            }
            
            try:
                self._make_request("POST", "/oauth2PermissionGrants", data=consent_data)
            except Exception as e:
                print(f"Error granting consent for permission {permission_id}: {e}")
                return False
                
        return True