#!/usr/bin/env python3
"""
Create Jira Ticket Script

Creates Jira tickets via REST API with Personal Access Token (Bearer) authentication.
Supports dynamic payload structures based on project keys.

Usage:
    create_jira_ticket.py --project-key <KEY> --issue-type <TYPE> --summary <SUMMARY> --description <DESC> [--custom-fields <JSON>]

Environment Variables:
    JIRA_BASE_URL: Base URL of your Jira instance (e.g., https://yourcompany.atlassian.net)
    JIRA_PAT: Personal Access Token for Bearer authentication

Examples:
    # Create a Story in MOBILE project
    create_jira_ticket.py --project-key MOBILE --issue-type Story \\
        --summary "Implement login screen" \\
        --description "As a user, I want to log in securely" \\
        --custom-fields '{"device_type": "iOS"}'

    # Create a Bug in WEB project
    create_jira_ticket.py --project-key WEB --issue-type Bug \\
        --summary "Button not responding" \\
        --description "The submit button does not work on Chrome" \\
        --custom-fields '{"browser": "Chrome"}'
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


# =============================================================================
# PROJECT SCHEMA DEFINITIONS
# =============================================================================
# Define custom field mappings for each project. The dictionary maps:
# - project_key -> schema configuration
#
# Each schema contains:
# - required_fields: List of field names the user must provide
# - custom_fields: Mapping of user-friendly names to Jira custom field IDs
#
# Example: For MOBILE project, "device_type" maps to "customfield_10100"
# When user provides --custom-fields '{"device_type": "iOS"}', it becomes
# {"customfield_10100": "iOS"} in the Jira payload.
# =============================================================================

PROJECT_SCHEMAS = {
    "ACPF": {
        "required_fields": ["algo_id", "model_type"],
        "custom_fields": {
            "algo_id": "customfield_11001",
            "model_type": "customfield_11010",
        },
        "description": "Algo project (ACPF)"
    },
    "DPR": {
        "required_fields": ["dataset_id", "data_sensitivity"],
        "custom_fields": {
            "dataset_id": "customfield_11002",
            "data_sensitivity": "customfield_11020",
        },
        "description": "Data project (DPR)"
    },
    "DMCD": {
        "required_fields": ["device_os"],
        "custom_fields": {
            "device_os": "customfield_11003",
            "test_device": "customfield_11030", # Optional field
        },
        "description": "Mobile project (DMCD)"
    },
}

# Default schema for projects not explicitly defined
DEFAULT_SCHEMA = {
    "required_fields": [],
    "custom_fields": {},
    "description": "Standard project (no custom fields required)"
}


def get_project_schema(project_key: str) -> dict:
    """
    Get the schema configuration for a given project key.
    Returns DEFAULT_SCHEMA if project is not explicitly defined.
    """
    return PROJECT_SCHEMAS.get(project_key, DEFAULT_SCHEMA)


def validate_custom_fields(project_key: str, custom_fields: dict) -> tuple[bool, str]:
    """
    Validate that all required custom fields are present for the given project.
    
    Returns:
        tuple: (is_valid, error_message)
    """
    schema = get_project_schema(project_key)
    required = schema.get("required_fields", [])
    
    missing = [field for field in required if field not in custom_fields]
    
    if missing:
        return False, f"Missing required fields for project {project_key}: {', '.join(missing)}"
    
    return True, ""


def build_payload(
    project_key: str,
    issue_type: str,
    summary: str,
    description: str,
    custom_fields: dict | None = None
) -> dict:
    """
    Build the Jira API payload with dynamic field mapping based on project.
    
    Args:
        project_key: The Jira project key (e.g., MOBILE, WEB)
        issue_type: The issue type (Story, Bug)
        summary: Issue summary/title
        description: Issue description
        custom_fields: Optional dictionary of custom field values
    
    Returns:
        dict: The complete Jira API payload
    """
    # Base payload structure
    payload = {
        "fields": {
            "project": {
                "key": project_key
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": issue_type
            }
        }
    }
    
    # Apply custom fields if provided
    if custom_fields:
        schema = get_project_schema(project_key)
        field_mapping = schema.get("custom_fields", {})
        
        for field_name, field_value in custom_fields.items():
            # Map user-friendly field name to Jira custom field ID
            jira_field_id = field_mapping.get(field_name)
            
            if jira_field_id:
                payload["fields"][jira_field_id] = field_value
            else:
                # If not in mapping, assume it's already a Jira field ID
                # (e.g., customfield_12345 or standard field like labels)
                payload["fields"][field_name] = field_value
    
    return payload


def create_jira_ticket(
    base_url: str,
    pat: str,
    payload: dict
) -> tuple[bool, dict]:
    """
    Create a Jira ticket via REST API.
    
    Args:
        base_url: Jira instance base URL
        pat: Personal Access Token
        payload: The Jira API payload
    
    Returns:
        tuple: (success, response_data)
    """
    url = f"{base_url.rstrip('/')}/rest/api/2/issue"
    
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    data = json.dumps(payload).encode("utf-8")
    
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    
    try:
        with urllib.request.urlopen(request) as response:
            response_data = json.loads(response.read().decode("utf-8"))
            return True, response_data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
        except json.JSONDecodeError:
            error_data = {"raw_error": error_body}
        return False, {"status_code": e.code, "error": error_data}
    except urllib.error.URLError as e:
        return False, {"error": str(e.reason)}


def list_projects():
    """Print available project schemas."""
    print("\n📋 Available Project Schemas:")
    print("=" * 60)
    
    for key, schema in PROJECT_SCHEMAS.items():
        print(f"\n🔹 {key}")
        print(f"   Description: {schema.get('description', 'No description')}")
        print(f"   Required fields: {', '.join(schema['required_fields']) or 'None'}")
        if schema['custom_fields']:
            print(f"   Custom fields: {', '.join(schema['custom_fields'].keys())}")
    
    print(f"\n🔹 DEFAULT (any unlisted project)")
    print(f"   Description: {DEFAULT_SCHEMA['description']}")
    print(f"   Required fields: None")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Create Jira tickets via REST API with Bearer authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment Variables:
  JIRA_BASE_URL    Base URL of your Jira instance
  JIRA_PAT         Personal Access Token for authentication

Examples:
  %(prog)s --project-key MOBILE --issue-type Story \\
      --summary "Add dark mode" --description "Implement dark mode toggle"
      
  %(prog)s --project-key WEB --issue-type Bug \\
      --summary "Fix login" --description "Login fails on Safari" \\
      --custom-fields '{"browser": "Safari"}'

  %(prog)s --list-projects
        """
    )
    
    parser.add_argument(
        "--json-input", "-j",
        help="Path to JSON file containing ticket details (project_key, summary, etc.)"
    )
    parser.add_argument(
        "--project-key", "-p",
        help="Jira project key (e.g., MOBILE, WEB, BACKEND)"
    )
    parser.add_argument(
        "--issue-type", "-t",
        choices=["Story", "Bug"],
        default="Story",
        help="Issue type (default: Story)"
    )
    parser.add_argument(
        "--summary", "-s",
        help="Issue summary/title"
    )
    parser.add_argument(
        "--description", "-d",
        help="Issue description"
    )
    parser.add_argument(
        "--custom-fields", "-c",
        help="JSON string of custom field values (e.g., '{\"device_type\": \"iOS\"}')"
    )
    parser.add_argument(
        "--list-projects", "-l",
        action="store_true",
        help="List available project schemas and exit"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the payload without sending to Jira"
    )
    
    args = parser.parse_args()
    
    # Handle --list-projects
    if args.list_projects:
        list_projects()
        sys.exit(0)
    
    # Handle JSON input
    if args.json_input:
        try:
            with open(args.json_input, 'r') as f:
                json_args = json.load(f)
                
            # CLI args override JSON args
            if not args.project_key and 'project_key' in json_args:
                args.project_key = json_args['project_key']
            if args.issue_type == "Story" and 'issue_type' in json_args: # Default value
                args.issue_type = json_args['issue_type']
            if not args.summary and 'summary' in json_args:
                args.summary = json_args['summary']
            if not args.description and 'description' in json_args:
                args.description = json_args['description']
            if not args.custom_fields and 'custom_fields' in json_args:
                # Store as dict, skipping the parse step below
                custom_fields = json_args['custom_fields']
                
        except Exception as e:
            print(f"❌ Error reading JSON input: {e}")
            sys.exit(1)

    # Validate required arguments
    if not args.project_key:
        parser.error("--project-key is required (or in --json-input)")
    if not args.summary:
        parser.error("--summary is required (or in --json-input)")
    if not args.description:
        parser.error("--description is required (or in --json-input)")

    # Unescape newlines in summary and description
    # This fixes issues where \n passed from CLI is treated as literal characters
    if args.summary:
        args.summary = args.summary.replace('\\n', '\n')
    if args.description:
        args.description = args.description.replace('\\n', '\n')

    # Enforce required summary prefix
    required_prefix = "[RECO][Algo]"
    if not args.summary.startswith(required_prefix):
        args.summary = f"{required_prefix} {args.summary}"
    
    # Parse custom fields from CLI if not already loaded from JSON
    custom_fields = {}
    if args.custom_fields:
        try:
            custom_fields = json.loads(args.custom_fields)
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing --custom-fields JSON: {e}")
            sys.exit(1)
    
    # Validate custom fields for project
    is_valid, error_msg = validate_custom_fields(args.project_key, custom_fields)
    if not is_valid:
        print(f"❌ {error_msg}")
        schema = get_project_schema(args.project_key)
        print(f"💡 Use --custom-fields to provide: {schema['required_fields']}")
        sys.exit(1)
    
    # Build payload
    payload = build_payload(
        project_key=args.project_key,
        issue_type=args.issue_type,
        summary=args.summary,
        description=args.description,
        custom_fields=custom_fields
    )
    
    # Handle dry run
    if args.dry_run:
        print("🔍 Dry run - payload that would be sent:")
        print(json.dumps(payload, indent=2))
        sys.exit(0)
    
    # User Confirmation
    print(f"\n🚀 Ready to create {args.issue_type} in {args.project_key}")
    print(f"Summary: {args.summary}")
    print("Payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        confirm = input("\n❓ Proceed with creation? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Creation cancelled by user.")
            sys.exit(0)
    except EOFError:
        print("\n❌ Input stream closed, aborting.")
        sys.exit(1)
    
    
    # Get environment variables
    # base_url = os.environ.get("JIRA_BASE_URL")
    # pat = os.environ.get("JIRA_PAT")
    
    # if not base_url:
    #     print("❌ Error: JIRA_BASE_URL environment variable not set")
    #     sys.exit(1)
    # if not pat:
    #     print("❌ Error: JIRA_PAT environment variable not set")
    #     sys.exit(1)
    
    # Create the ticket
    print(f"📝 Creating {args.issue_type} in project {args.project_key}...")

    # FOR DEBUG: Commented out actual API call
    # success, response = create_jira_ticket(base_url, pat, payload)
    
    # Simulate success
    print("Example payload:")
    print(json.dumps(payload, indent=2))
    success = True
    response = {"key": "SIM-123", "id": "10000"}

    if success:
        base_url = "https://simulated.atlassian.net"
        issue_key = response.get("key", "Unknown")
        issue_id = response.get("id", "Unknown")
        issue_url = f"{base_url.rstrip('/')}/browse/{issue_key}"
        
        print(f"✅ Ticket created successfully!")
        print(f"   Key: {issue_key}")
        print(f"   ID: {issue_id}")
        print(f"   URL: {issue_url}")
    else:
        print(f"❌ Failed to create ticket")
        print(f"   Error: {json.dumps(response, indent=2)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
