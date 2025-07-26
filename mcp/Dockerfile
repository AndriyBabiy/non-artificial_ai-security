FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies directly
RUN pip install \
    "fastapi>=0.104.0" \
    "uvicorn[standard]>=0.24.0" \
    "requests>=2.31.0" \
    "python-dotenv>=1.0.0" \
    "pydantic>=2.5.0" \
    "httpx>=0.25.0" \
    "cryptography>=41.0.0" \
    "dnspython>=2.4.0"

# Copy source code (only files that exist)
COPY main.py .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]