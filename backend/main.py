from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
import requests
import os
from dotenv import load_dotenv
import json
from typing import Dict, Any, List

load_dotenv()

app = FastAPI(title="Security Scanner Backend", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://172.201.157.195/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize LLM with correct Gemini model
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise ValueError("Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable")

# Use the correct model name - try these in order of preference
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  # This is the current fast model
        temperature=0,
        google_api_key=api_key
    )
except Exception as e:
    print(f"Failed to load gemini-1.5-flash, trying gemini-1.5-pro: {e}")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",  # Fallback to pro model
            temperature=0,
            google_api_key=api_key
        )
    except Exception as e2:
        print(f"Failed to load gemini-1.5-pro, trying gemini-pro: {e2}")
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",  # Last resort
            temperature=0,
            google_api_key=api_key
        )

MCP_URL = os.getenv("MCP_URL", "http://localhost:8001")

class ScanRequest(BaseModel):
    url: str = Field(..., description="The URL to scan (without protocol)")
    prompt: str = Field(default="Check for security breaches", description="Custom scan instructions")

class ScanResponse(BaseModel):
    results: Dict[str, Any]
    summary: str

# Define tools that call MCP server
@tool
def check_ssl_certificate(url: str, check_chain: bool = True) -> dict:
    """Check SSL certificate validity and configuration."""
    try:
        response = requests.post(
            f"{MCP_URL}/check_ssl", 
            json={"url": url, "check_chain": check_chain},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"SSL check failed: {str(e)}"}

@tool
def scan_vulnerabilities(url: str, scan_depth: str = "light") -> dict:
    """Scan for common web vulnerabilities."""
    try:
        response = requests.post(
            f"{MCP_URL}/scan_vulnerabilities", 
            json={"url": url, "scan_depth": scan_depth},
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Vulnerability scan failed: {str(e)}"}

@tool
def analyze_security_headers(url: str) -> dict:
    """Analyze HTTP security headers."""
    try:
        response = requests.post(
            f"{MCP_URL}/analyze_security_headers", 
            json={"url": url},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Security headers analysis failed: {str(e)}"}

# Available tools
tools = [check_ssl_certificate, scan_vulnerabilities, analyze_security_headers]

@app.post("/scan", response_model=ScanResponse)
async def scan_website(request: ScanRequest):
    """Main endpoint to scan a website for security issues."""
    try:
        # Clean URL
        url = request.url.strip().lower()
        url = url.replace("http://", "").replace("https://", "")
        
        # Run all tools directly (simplified approach since Gemini tool calling can be tricky)
        print(f"Starting scan for {url}")
        
        # Execute all security checks
        ssl_result = check_ssl_certificate(url)
        vuln_result = scan_vulnerabilities(url)
        headers_result = analyze_security_headers(url)
        
        aggregated_results = {
            "ssl": ssl_result,
            "vulnerabilities": vuln_result,
            "security_headers": headers_result
        }
        
        print(f"Scan results: {aggregated_results}")

        # Generate summary with LLM
        summary_prompt = f"""
Analyze these security scan results for the website {url}:

SSL Certificate Check:
{json.dumps(ssl_result, indent=2)}

Vulnerability Scan:
{json.dumps(vuln_result, indent=2)}

Security Headers Analysis:
{json.dumps(headers_result, indent=2)}

Please provide a comprehensive security assessment including:
1. Overall security rating (Excellent/Good/Fair/Poor/Critical)
2. Key security findings
3. Critical vulnerabilities that need immediate attention
4. Recommended improvements
5. Priority action items

Keep the summary clear and actionable.
"""

        print("Generating AI summary...")
        summary_response = llm.invoke(summary_prompt)
        summary = summary_response.content if hasattr(summary_response, 'content') else str(summary_response)
        print(f"AI summary generated: {summary[:100]}...")

        return ScanResponse(
            results=aggregated_results,
            summary=summary
        )

    except Exception as e:
        print(f"Scan error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "security-scanner-backend"}

@app.get("/test-llm")
async def test_llm():
    """Test endpoint to verify LLM is working."""
    try:
        response = llm.invoke("Hello, please respond with 'LLM is working correctly'")
        return {"status": "success", "response": response.content}
    except Exception as e:
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
