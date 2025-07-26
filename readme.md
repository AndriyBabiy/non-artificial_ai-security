# Website Security Scanner

A comprehensive security scanning tool built with Next.js frontend, FastAPI backend, and MCP (Model Context Protocol) server architecture.

## Architecture

- **Frontend**: Next.js with TypeScript and Tailwind CSS
- **Backend**: FastAPI with LangChain for LLM orchestration
- **MCP Server**: FastAPI server exposing security check functions
- **LLM Integration**: Supports OpenAI GPT-4 or Grok for tool calling

## Features

- SSL Certificate validation
- Vulnerability scanning
- Security headers analysis
- LLM-powered scan orchestration
- Responsive web interface

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+ and uv (Python package manager)
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key or Grok API key

## Quick Start

### Option 1: Docker Compose (Recommended)

1. **Clone and setup**:

   ```bash
   git clone <your-repo-url>
   cd website-security-scanner
   cp .env.example .env
   ```

2. **Configure environment**:
   Edit `.env` and add your LLM API key:

   ```
   OPENAI_API_KEY=your-openai-key-here
   # OR
   GEMINI_API_KEY=your-gemini-key-here
   ```

3. **Run with Docker**:

   ```bash
   docker-compose up --build
   ```

4. **Access the application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - MCP Server: http://localhost:8001

### Option 2: Local Development

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

#### Backend Setup

```bash
cd backend
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
cp .env.example .env  # Add your API keys
uvicorn main:app --port 8000 --reload
```

#### MCP Server Setup

```bash
cd mcp
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
uvicorn main:app --port 8001 --reload
```

## Usage

1. Open http://localhost:3000
2. Enter a website URL (e.g., `example.com`)
3. Optionally modify the prompt (default: "Check for security breaches")
4. Click "Scan" to start the security analysis
5. View the aggregated results and AI-generated summary

## API Endpoints

### Backend (`localhost:8000`)

- `POST /scan` - Main scanning endpoint

### MCP Server (`localhost:8001`)

- `POST /check_ssl` - SSL certificate validation
- `POST /scan_vulnerabilities` - Vulnerability scanning
- `POST /analyze_security_headers` - Security headers analysis

## Development

### Adding New Security Checks

1. **Add MCP endpoint** in `mcp/main.py`:

   ```python
   @app.post("/new_check")
   async def new_check(req: NewCheckRequest):
       # Implementation
       return {"result": "data"}
   ```

2. **Add tool in backend** `backend/main.py`:

   ```python
   @tool
   def new_check_tool(url: str) -> dict:
       """Description of the check."""
       response = requests.post("http://localhost:8001/new_check", json={"url": url})
       return response.json()
   ```

3. **Register tool** in the tools list.

### Testing

```bash
# Frontend
cd frontend && npm test

# Backend
cd backend && uv run pytest

# MCP
cd mcp && uv run pytest
```

## Deployment

### Production Environment Variables

Create production `.env` files:

- Set secure API keys
- Update CORS origins for frontend domain
- Configure database connections if added

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up --build
```

### Platform Deployment

- **Frontend**: Deploy to Vercel, Netlify, or similar
- **Backend/MCP**: Deploy to Railway, Render, or AWS ECS
- **Environment**: Use platform-specific environment variable management

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and test locally
4. Submit a pull request

## Security Considerations

- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- Implement rate limiting in production
- Add authentication for production deployments
- Validate and sanitize all user inputs

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 3000, 8000, 8001 are available
2. **API key errors**: Verify your LLM API key is correctly set in `.env`
3. **CORS errors**: Check that backend CORS settings include your frontend URL
4. **Docker issues**: Run `docker-compose down -v` to clean volumes

### Logs

```bash
# View logs for specific service
docker-compose logs frontend
docker-compose logs backend
docker-compose logs mcp
```

For more help, please open an issue on GitHub.
