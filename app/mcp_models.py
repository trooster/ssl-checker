"""
Pydantic models for MCP server data structures
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class Certificate(BaseModel):
    """Represents an SSL certificate"""
    id: int
    fqdn: str
    customer_number: Optional[str] = None
    customer_name: Optional[str] = None
    issuer: Optional[str] = None
    issuer_type: Optional[str] = None
    expiry_date: Optional[str] = None
    days_remaining: Optional[int] = None
    checked_at: Optional[str] = None
    status: Optional[str] = None


class CertificateDetails(BaseModel):
    """Extended certificate details"""
    fqdn: str
    issuer: str
    issuer_type: str
    expiry_date: str
    days_remaining: Optional[int] = None
    not_before: Optional[str] = None
    serial_number: Optional[str] = None
    version: Optional[int] = None
    subject_cn: Optional[str] = None
    subject: Optional[dict] = None
    issuer_details: Optional[dict] = None
    fingerprint_sha256: Optional[str] = None
    san_string: Optional[str] = None


class CertificateQuery(BaseModel):
    """Query parameters for certificate searches"""
    days: Optional[int] = None
    customer_name: Optional[str] = None


class CertificateAdd(BaseModel):
    """DTO for adding a new certificate"""
    fqdn: str
    customer_number: Optional[str] = None
    customer_name: Optional[str] = None


class CertificateResponse(BaseModel):
    """Response to certificate operations"""
    success: bool
    message: str
    certificate: Optional[Certificate] = None
    certificates: Optional[List[Certificate]] = None
    count: Optional[int] = None


class McpServerStatus(BaseModel):
    """Server status information"""
    status: str
    version: str
    uptime: Optional[int] = None
    certificates_monitored: Optional[int] = None
