#!/usr/bin/env python3
"""
MCP server for SSL Certificate Monitor
Runs as a standalone server communicating via stdio
"""
import json
import sys
import requests


def send_response(response_data):
    """Send response to MCP client"""
    print(json.dumps(response_data))
    sys.stdout.flush()


def handle_request(request_msg):
    """Handle an MCP request"""
    try:
        msg = json.loads(request_msg.strip())
        
        if msg.get('type') == 'initialize':
            return {
                "jsonrpc": "2.0",
                "id": msg.get('id'),
                "result": {
                    "serverInfo": {
                        "name": "ssl-cert-monitor",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {}
                    }
                }
            }
        
        elif msg.get('type') == 'tools/list':
            return {
                "jsonrpc": "2.0",
                "id": msg.get('id'),
                "result": {
                    "tools": [
                        {
                            "name": "add_certificate",
                            "description": "Add a new SSL certificate to monitor",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "fqdn": {"type": "string", "description": "Fully qualified domain name"},
                                    "customer_number": {"type": "string", "description": "Optional customer number"},
                                    "customer_name": {"type": "string", "description": "Optional customer name"}
                                },
                                "required": ["fqdn"]
                            }
                        },
                        {
                            "name": "list_certificates",
                            "description": "List all monitored SSL certificates",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "sort_by": {"type": "string", "enum": ["expiry", "customer_name", "fqdn"], "default": "expiry"},
                                    "sort_order": {"type": "string", "enum": ["asc", "desc"], "default": "asc"},
                                    "limit": {"type": "integer", "default": 100}
                                }
                            }
                        },
                        {
                            "name": "query_expiring",
                            "description": "Get certificates expiring within specified days",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "days": {"type": "integer", "default": 30}
                                }
                            }
                        },
                        {
                            "name": "query_expired",
                            "description": "Get all expired certificates"
                        },
                        {
                            "name": "query_customer",
                            "description": "Get certificates for specific customer",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "customer_name": {"type": "string"}
                                },
                                "required": ["customer_name"]
                            }
                        },
                        {
                            "name": "refresh_certificate",
                            "description": "Manually refresh SSL certificate information",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "fqdn": {"type": "string"}
                                },
                                "required": ["fqdn"]
                            }
                        },
                        {
                            "name": "get_certificate_details",
                            "description": "Get full certificate details for a domain",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "fqdn": {"type": "string"}
                                },
                                "required": ["fqdn"]
                            }
                        },
                        {
                            "name": "delete_certificate",
                            "description": "Delete a certificate from monitoring",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "fqdn": {"type": "string"}
                                },
                                "required": ["fqdn"]
                            }
                        },
                        {
                            "name": "get_server_status",
                            "description": "Get MCP server status information"
                        }
                    ]
                }
            }
        
        elif msg.get('type') == 'tools/call':
            tool_name = msg.get('tool_name')
            tool_args = msg.get('arguments', {})
            
            return {
                "jsonrpc": "2.0",
                "id": msg.get('id'),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(call_tool(tool_name, tool_args), indent=2)
                        }
                    ]
                }
            }
        
        return {
            "jsonrpc": "2.0",
            "id": msg.get('id'),
            "error": {
                "code": -32601,
                "message": "Unknown request type"
            }
        }
    
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }


def call_tool(tool_name, args):
    """Call an MCP tool"""
    base_url = "http://localhost:4444"
    
    try:
        if tool_name == "add_certificate":
            response = requests.post(
                f"{base_url}/api/urls",
                json={"fqdn": args.get("fqdn"), "customer_number": args.get("customer_number", ""), "customer_name": args.get("customer_name", "")}
            )
            return {"success": True, "data": response.json()}
        
        elif tool_name == "list_certificates":
            sort_by = args.get("sort_by", "expiry")
            sort_order = args.get("sort_order", "asc")
            limit = args.get("limit", 100)
            response = requests.get(f"{base_url}/api/urls?sort_by={sort_by}&sort_order={sort_order}")
            return {"success": True, "data": response.json()}
        
        elif tool_name == "query_expiring":
            days = args.get("days", 30)
            response = requests.get(f"{base_url}/api/query/expiring?days={days}")
            return {"success": True, "data": response.json()}
        
        elif tool_name == "query_expired":
            response = requests.get(f"{base_url}/api/query/expired")
            return {"success": True, "data": response.json()}
        
        elif tool_name == "query_customer":
            customer_name = args.get("customer_name", "")
            import urllib.parse
            encoded_name = urllib.parse.quote(customer_name)
            response = requests.get(f"{base_url}/api/query/customer?name={encoded_name}")
            return {"success": True, "data": response.json()}
        
        elif tool_name == "refresh_certificate":
            fqdn = args.get("fqdn", "")
            response = requests.post(f"{base_url}/api/certs/{fqdn}/refresh")
            return {"success": True, "data": response.json()}
        
        elif tool_name == "get_certificate_details":
            fqdn = args.get("fqdn", "")
            response = requests.get(f"{base_url}/api/certs/{fqdn}/details")
            return {"success": True, "data": response.json()}
        
        elif tool_name == "delete_certificate":
            fqdn = args.get("fqdn", "")
            import urllib.parse
            encoded_fqdn = urllib.parse.quote(fqdn)
            response = requests.delete(f"{base_url}/api/urls?fqdn={encoded_fqdn}")
            return {"success": True, "data": response.json()}
        
        elif tool_name == "get_server_status":
            response = requests.get(f"{base_url}/api/status")
            return {"success": True, "data": response.json()}
        
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
    
    except Exception as e:
        return {"success": False, "error": str(e)}


def main():
    """Main MCP server loop"""
    print("SSL Certificate Monitor MCP Server")
    print("Tools available:")
    print("  - add_certificate")
    print("  - list_certificates")
    print("  - query_expiring")
    print("  - query_expired")
    print("  - query_customer")
    print("  - refresh_certificate")
    print("  - get_certificate_details")
    print("  - delete_certificate")
    print("  - get_server_status")
    print("\nWaiting for MCP requests...")
    print("To test: echo '{.}' | python3 app/mcp_server.py")
    
    # Simple echo loop for testing
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            response = handle_request(line)
            print(json.dumps(response))
            sys.stdout.flush()
        
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
