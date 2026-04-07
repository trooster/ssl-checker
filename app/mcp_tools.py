"""
MCP tool definitions for SSL Certificate Monitor
"""
from typing import List, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, CallToolResult


class SSLCertTools:
    """MCP tools for SSL certificate operations"""
    
    def __init__(self, server: Server):
        self.server = server
    
    def define_tools(self) -> List[Tool]:
        """Define all MCP tools"""
        return [
            Tool(
                name="add_certificate",
                description="Add a new SSL certificate to monitor",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fqdn": {"type": "string", "description": "Fully qualified domain name"},
                        "customer_number": {"type": "string", "description": "Optional customer number"},
                        "customer_name": {"type": "string", "description": "Optional customer name"}
                    },
                    "required": ["fqdn"]
                }
            ),
            Tool(
                name="list_certificates",
                description="List all monitored SSL certificates",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "sort_by": {"type": "string", "enum": ["expiry", "customer_name", "fqdn"], "default": "expiry"},
                        "sort_order": {"type": "string", "enum": ["asc", "desc"], "default": "asc"},
                        "limit": {"type": "integer", "default": 100}
                    }
                }
            ),
            Tool(
                name="query_expiring",
                description="Get certificates expiring within specified days",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "days": {"type": "integer", "default": 30}
                    }
                }
            ),
            Tool(
                name="query_expired",
                description="Get all expired certificates"
            ),
            Tool(
                name="query_customer",
                description="Get certificates for specific customer",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string"}
                    },
                    "required": ["customer_name"]
                }
            ),
            Tool(
                name="refresh_certificate",
                description="Manually refresh SSL certificate information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fqdn": {"type": "string"}
                    },
                    "required": ["fqdn"]
                }
            ),
            Tool(
                name="get_certificate_details",
                description="Get full certificate details for a domain",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fqdn": {"type": "string"}
                    },
                    "required": ["fqdn"]
                }
            ),
            Tool(
                name="delete_certificate",
                description="Delete a certificate from monitoring",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fqdn": {"type": "string"}
                    },
                    "required": ["fqdn"]
                }
            ),
            Tool(
                name="get_server_status",
                description="Get MCP server status information"
            )
        ]
