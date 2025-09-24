######## ServiceNow MCP Server - MCR-compliant Dockerfile

FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm AS runtime
WORKDIR /app

# Core runtime defaults
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SERVICENOW_DEBUG=false \
    SERVICENOW_TIMEOUT=30 \
    SERVICENOW_AUTH_TYPE=basic

ENV TOOL_PACKAGE_CONFIG_PATH=/app/config/tool_packages.yaml

# Copy project
COPY . .

# Install package into system Python
RUN pip install --no-cache-dir .

# Non-root user (devcontainer images default to vscode)
USER 1000:1000

EXPOSE 8080

# Start SSE-compatible HTTP server
CMD ["servicenow-mcp-sse", "--host=0.0.0.0", "--port=8080"]