from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests
import ssl
import socket
from urllib.parse import urlparse
import dns.resolver
from datetime import datetime, timezone
import json
from typing import Dict, List, Any, Optional

app = FastAPI(title="Security Scanner MCP Server", version="0.1.0")

# Request models
class SSLRequest(BaseModel):
    url: str = Field(..., description="Domain to check SSL certificate")
    check_chain: bool = Field(default=True, description="Whether to validate certificate chain")

class VulnerabilityRequest(BaseModel):
    url: str = Field(..., description="URL to scan for vulnerabilities")
    scan_depth: str = Field(default="light", description="Scan depth: light, medium, or deep")

class SecurityHeadersRequest(BaseModel):
    url: str = Field(..., description="URL to analyze security headers")

class PortScanRequest(BaseModel):
    url: str = Field(..., description="Domain to scan ports")
    ports: Optional[List[int]] = Field(default=None, description="Specific ports to scan")

class DNSRequest(BaseModel):
    domain: str = Field(..., description="Domain to analyze DNS records")

# Utility functions
def clean_url(url: str) -> str:
    """Clean and normalize URL."""
    url = url.strip().lower()
    url = url.replace("http://", "").replace("https://", "")
    if "/" in url:
        url = url.split("/")[0]
    return url

def get_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    parsed = urlparse(url)
    return parsed.netloc or parsed.path.split('/')[0]

@app.post("/check_ssl")
async def check_ssl_certificate(request: SSLRequest):
    """Check SSL certificate validity and configuration."""
    try:
        domain = clean_url(request.url)
        
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and get certificate
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                cert_der = ssock.getpeercert(binary_form=True)
                
        # Parse certificate information
        subject = dict(x[0] for x in cert.get('subject', []))
        issuer = dict(x[0] for x in cert.get('issuer', []))
        
        # Check expiration
        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
        not_before = datetime.strptime(cert['notBefore'], '%b %d %H:%M:%S %Y %Z')
        days_until_expiry = (not_after - datetime.now()).days
        
        # Basic security checks
        issues = []
        if days_until_expiry < 30:
            issues.append(f"Certificate expires in {days_until_expiry} days")
        if 'CN' not in subject:
            issues.append("No Common Name in certificate")
        
        # Check Subject Alternative Names
        san_list = []
        for ext in cert.get('extensions', []):
            if 'subjectAltName' in str(ext):
                san_list = [name.split(':')[1] for name in str(ext).split(', ') if ':' in name]
        
        result = {
            "valid": True,
            "domain": domain,
            "subject": subject,
            "issuer": issuer,
            "not_before": not_before.isoformat(),
            "not_after": not_after.isoformat(),
            "days_until_expiry": days_until_expiry,
            "subject_alt_names": san_list,
            "issues": issues,
            "chain_valid": request.check_chain  # Simplified - real implementation would verify chain
        }
        
        return result
        
    except socket.timeout:
        return {"valid": False, "error": "Connection timeout", "domain": request.url}
    except socket.gaierror:
        return {"valid": False, "error": "Domain not found", "domain": request.url}
    except ssl.SSLError as e:
        return {"valid": False, "error": f"SSL error: {str(e)}", "domain": request.url}
    except Exception as e:
        return {"valid": False, "error": f"Unexpected error: {str(e)}", "domain": request.url}

@app.post("/scan_vulnerabilities")
async def scan_vulnerabilities(request: VulnerabilityRequest):
    """Scan for common web vulnerabilities."""
    try:
        url = request.url
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        vulnerabilities = []
        score = 10.0  # Start with perfect score
        
        # Basic HTTP request to gather info
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            headers = response.headers
            content = response.text.lower()
            
            # Check for common vulnerabilities based on headers and content
            
            # Missing security headers
            security_headers = {
                'x-frame-options': 'Clickjacking protection missing',
                'x-content-type-options': 'MIME-sniffing protection missing',
                'x-xss-protection': 'XSS protection header missing',
                'strict-transport-security': 'HSTS header missing',
                'content-security-policy': 'CSP header missing'
            }
            
            for header, description in security_headers.items():
                if header not in [h.lower() for h in headers.keys()]:
                    vulnerabilities.append({
                        "type": "Missing Security Header",
                        "severity": "medium",
                        "description": description,
                        "header": header
                    })
                    score -= 0.5
            
            # Check for information disclosure
            if 'server' in headers:
                server_info = headers['server']
                if any(tech in server_info.lower() for tech in ['apache', 'nginx', 'iis']):
                    vulnerabilities.append({
                        "type": "Information Disclosure",
                        "severity": "low",
                        "description": f"Server information disclosed: {server_info}",
                        "detail": server_info
                    })
                    score -= 0.2
            
            # Basic content checks
            if 'sql' in content and 'error' in content:
                vulnerabilities.append({
                    "type": "Potential SQL Error",
                    "severity": "medium",
                    "description": "Possible SQL error messages in content"
                })
                score -= 1.0
                
            if request.scan_depth in ['medium', 'deep']:
                # Additional checks for deeper scans
                
                # Check for common vulnerable paths
                vulnerable_paths = ['/admin', '/wp-admin', '/.env', '/config.php']
                for path in vulnerable_paths:
                    try:
                        test_response = requests.get(url + path, timeout=5)
                        if test_response.status_code == 200:
                            vulnerabilities.append({
                                "type": "Exposed Endpoint",
                                "severity": "high",
                                "description": f"Potentially sensitive endpoint accessible: {path}",
                                "path": path,
                                "status_code": test_response.status_code
                            })
                            score -= 1.5
                    except:
                        pass  # Path not accessible or timeout
                        
                # Check for directory listing
                try:
                    dir_response = requests.get(url.rstrip('/') + '/', timeout=5)
                    if 'index of' in dir_response.text.lower():
                        vulnerabilities.append({
                            "type": "Directory Listing",
                            "severity": "medium",
                            "description": "Directory listing may be enabled"
                        })
                        score -= 0.8
                except:
                    pass
                    
            if request.scan_depth == 'deep':
                # Most comprehensive checks
                
                # Check for HTTP methods
                try:
                    options_response = requests.options(url, timeout=5)
                    if 'allow' in options_response.headers:
                        allowed_methods = options_response.headers['allow']
                        dangerous_methods = ['TRACE', 'DELETE', 'PUT']
                        for method in dangerous_methods:
                            if method in allowed_methods.upper():
                                vulnerabilities.append({
                                    "type": "Dangerous HTTP Method",
                                    "severity": "medium",
                                    "description": f"Dangerous HTTP method enabled: {method}",
                                    "method": method
                                })
                                score -= 0.5
                except:
                    pass
                    
        except requests.RequestException as e:
            return {
                "error": f"Could not connect to {url}: {str(e)}",
                "vulnerabilities": [],
                "score": 0.0
            }
        
        # Ensure score doesn't go below 0
        score = max(0.0, score)
        
        # Determine overall risk level
        if score >= 8.0:
            risk_level = "low"
        elif score >= 6.0:
            risk_level = "medium"
        elif score >= 4.0:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return {
            "url": url,
            "scan_depth": request.scan_depth,
            "vulnerabilities": vulnerabilities,
            "vulnerability_count": len(vulnerabilities),
            "security_score": round(score, 1),
            "risk_level": risk_level,
            "scan_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {"error": f"Vulnerability scan failed: {str(e)}"}

@app.post("/analyze_security_headers")
async def analyze_security_headers(request: SecurityHeadersRequest):
    """Analyze HTTP security headers."""
    try:
        url = request.url
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        response = requests.get(url, timeout=10, allow_redirects=True)
        headers = response.headers
        
        # Define security headers and their importance
        security_headers_check = {
            'strict-transport-security': {
                'name': 'HTTP Strict Transport Security (HSTS)',
                'importance': 'high',
                'description': 'Prevents protocol downgrade attacks'
            },
            'content-security-policy': {
                'name': 'Content Security Policy (CSP)',
                'importance': 'high',
                'description': 'Prevents XSS and data injection attacks'
            },
            'x-frame-options': {
                'name': 'X-Frame-Options',
                'importance': 'medium',
                'description': 'Prevents clickjacking attacks'
            },
            'x-content-type-options': {
                'name': 'X-Content-Type-Options',
                'importance': 'medium',
                'description': 'Prevents MIME-sniffing attacks'
            },
            'x-xss-protection': {
                'name': 'X-XSS-Protection',
                'importance': 'low',
                'description': 'Legacy XSS protection (deprecated but still useful)'
            },
            'referrer-policy': {
                'name': 'Referrer Policy',
                'importance': 'medium',
                'description': 'Controls referrer information'
            },
            'permissions-policy': {
                'name': 'Permissions Policy',
                'importance': 'medium',
                'description': 'Controls browser features and APIs'
            }
        }
        
        present_headers = {}
        missing_headers = []
        
        # Check each security header
        for header_name, header_info in security_headers_check.items():
            header_value = None
            # Case-insensitive search
            for h, v in headers.items():
                if h.lower() == header_name:
                    header_value = v
                    break
                    
            if header_value:
                present_headers[header_name] = {
                    'value': header_value,
                    'name': header_info['name'],
                    'importance': header_info['importance'],
                    'description': header_info['description']
                }
            else:
                missing_headers.append({
                    'header': header_name,
                    'name': header_info['name'],
                    'importance': header_info['importance'],
                    'description': header_info['description']
                })
        
        # Calculate security score
        total_headers = len(security_headers_check)
        present_count = len(present_headers)
        score = (present_count / total_headers) * 10
        
        # Adjust score based on importance
        high_importance = [h for h, info in security_headers_check.items() if info['importance'] == 'high']
        high_present = [h for h in present_headers.keys() if h in high_importance]
        
        if len(high_present) == len(high_importance):
            score += 1  # Bonus for having all high-importance headers
        elif len(high_present) == 0:
            score -= 2  # Penalty for missing all high-importance headers
            
        score = max(0, min(10, score))  # Clamp between 0 and 10
        
        # Determine grade
        if score >= 9:
            grade = 'A'
        elif score >= 7:
            grade = 'B'
        elif score >= 5:
            grade = 'C'
        elif score >= 3:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            "url": url,
            "security_score": round(score, 1),
            "grade": grade,
            "present_headers": present_headers,
            "missing_headers": missing_headers,
            "total_headers_checked": total_headers,
            "headers_present": present_count,
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "recommendations": [
                f"Implement {h['name']}" for h in missing_headers if h['importance'] == 'high'
            ]
        }
        
    except requests.RequestException as e:
        return {"error": f"Could not analyze headers for {request.url}: {str(e)}"}
    except Exception as e:
        return {"error": f"Header analysis failed: {str(e)}"}

@app.post("/scan_ports")
async def scan_ports(request: PortScanRequest):
    """Basic port scanning functionality."""
    try:
        domain = clean_url(request.url)
        ports_to_scan = request.ports or [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
        
        open_ports = []
        closed_ports = []
        
        for port in ports_to_scan:
            try:
                with socket.create_connection((domain, port), timeout=3):
                    open_ports.append(port)
            except (socket.timeout, socket.error):
                closed_ports.append(port)
        
        # Analyze findings
        security_concerns = []
        if 21 in open_ports:
            security_concerns.append("FTP port 21 is open - consider using SFTP instead")
        if 23 in open_ports:
            security_concerns.append("Telnet port 23 is open - unencrypted protocol")
        if 80 in open_ports and 443 not in open_ports:
            security_concerns.append("Only HTTP (port 80) available - no HTTPS")
            
        return {
            "domain": domain,
            "open_ports": open_ports,
            "closed_ports": closed_ports,
            "total_scanned": len(ports_to_scan),
            "security_concerns": security_concerns,
            "scan_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {"error": f"Port scan failed: {str(e)}"}

@app.post("/analyze_dns")
async def analyze_dns(request: DNSRequest):
    """Analyze DNS records for security insights."""
    try:
        domain = request.domain.strip().lower()
        domain = domain.replace("http://", "").replace("https://", "")
        if "/" in domain:
            domain = domain.split("/")[0]
            
        dns_info = {}
        security_issues = []
        
        # Check different record types
        record_types = ['A', 'AAAA', 'MX', 'TXT', 'NS', 'CNAME']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(domain, record_type)
                dns_info[record_type] = [str(answer) for answer in answers]
            except dns.resolver.NoAnswer:
                dns_info[record_type] = []
            except Exception:
                dns_info[record_type] = ["Error resolving"]
        
        # Security analysis
        # Check for SPF record
        spf_found = False
        dmarc_found = False
        
        for txt_record in dns_info.get('TXT', []):
            if txt_record.startswith('"v=spf1'):
                spf_found = True
            if txt_record.startswith('"v=DMARC1'):
                dmarc_found = True
                
        if not spf_found:
            security_issues.append("No SPF record found - email spoofing protection missing")
        if not dmarc_found:
            security_issues.append("No DMARC record found - email authentication policy missing")
            
        # Check for too many A records (potential security risk)
        if len(dns_info.get('A', [])) > 5:
            security_issues.append("Many A records found - potential load balancing or CDN setup")
            
        return {
            "domain": domain,
            "dns_records": dns_info,
            "security_issues": security_issues,
            "spf_configured": spf_found,
            "dmarc_configured": dmarc_found,
            "scan_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {"error": f"DNS analysis failed: {str(e)}"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "security-scanner-mcp"}

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Security Scanner MCP Server",
        "version": "0.1.0",
        "endpoints": [
            "/check_ssl",
            "/scan_vulnerabilities", 
            "/analyze_security_headers",
            "/scan_ports",
            "/analyze_dns"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)