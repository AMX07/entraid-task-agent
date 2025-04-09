#!/usr/bin/env python3
import sys
import json
import argparse
from app_orchestrator import EntraIDAgent

def main():
    """Command-line interface for the Entra ID Agent."""
    
    parser = argparse.ArgumentParser(
        description="Process natural language commands for Entra ID operations"
    )
    parser.add_argument(
        "command", 
        nargs="+", 
        help="Natural language command to process (e.g., 'Create an app registration named MyApp')"
    )
    parser.add_argument(
        "--json", 
        action="store_true",
        help="Output results in JSON format"
    )
    
    args = parser.parse_args()
    
    # Join the command arguments into a single string
    command_text = " ".join(args.command)
    
    try:
        # Initialize the agent
        agent = EntraIDAgent()
        
        # Process the command
        result = agent.process_command(command_text)
        
        # Output the result
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get('success', False):
                print(f"\n✅ {result.get('message', 'Command processed successfully')}")
                
                # Print data if present
                if 'data' in result:
                    print("\nDetails:")
                    for key, value in result['data'].items():
                        # Mask client secret for security (just show first few chars)
                        if key == 'clientSecret' and value:
                            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:]
                            print(f"  {key}: {masked_value}")
                        else:
                            print(f"  {key}: {value}")
                
                # Print next steps if present
                if 'nextSteps' in result:
                    print("\nNext Steps:")
                    for step in result['nextSteps']:
                        print(f"  - {step}")
            else:
                print(f"\n❌ {result.get('message', 'An error occurred during processing')}")
                
        # Return appropriate exit code
        sys.exit(0 if result.get('success', False) else 1)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()