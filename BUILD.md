# Build and Push Instructions (ServiceNow MCP)

## Build the Image

```bash
docker build -f Dockerfile.mcr -t docker.io/xyfo/servicenow-mcp:latest .
```

## Push to Docker Hub

```bash
# docker login --username xyfo
docker push docker.io/xyfo/servicenow-mcp:latest
```

## Run Locally (HTTP/SSE)

```bash
docker run --rm -p 8080:8080 \
  -e SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com \
  -e SERVICENOW_USERNAME=your-username \
  -e SERVICENOW_PASSWORD=your-password \
  -e SERVICENOW_AUTH_TYPE=basic \
  docker.io/xyfo/servicenow-mcp:latest
```

## Notes

- The container runs as UID 1000 and exposes port 8080.
- `k8s/deployment.yaml` already points to `docker.io/xyfo/servicenow-mcp:latest`; bump the tag when you publish updates.
- Supply credentials via Kubernetes secrets or local env files; never bake them into the image.
