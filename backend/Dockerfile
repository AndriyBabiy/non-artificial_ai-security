FROM python:3.11-slim

WORKDIR /app

# Install dependencies directly
RUN pip install \
    "fastapi>=0.104.0" \
    "uvicorn[standard]>=0.24.0" \
    "langchain>=0.0.340" \
    "langchain-google-genai>=0.0.11" \
    "requests>=2.31.0" \
    "python-dotenv>=1.0.0" \
    "pydantic>=2.5.0" \
    "httpx>=0.25.0"

# Copy source code
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]