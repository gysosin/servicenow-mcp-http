"""
ServiceNow MCP Streamable HTTP Server

This module exposes the ServiceNow MCP server over the Streamable HTTP transport
so that clients can communicate via the standard `/mcp` endpoint.
"""

import argparse
import logging
import os
from typing import Dict, Union

import uvicorn
from dotenv import load_dotenv
from mcp.server import Server

try:
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
except ModuleNotFoundError:
    from servicenow_mcp.utils._streamable_http_manager_compat import StreamableHTTPSessionManager

from starlette.applications import Starlette
from starlette.routing import Route
from starlette.types import Receive, Scope, Send

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


logger = logging.getLogger(__name__)


class _StreamableHTTPASGIApp:
    """Minimal ASGI wrapper that proxies requests to the Streamable HTTP manager."""

    def __init__(self, session_manager: StreamableHTTPSessionManager) -> None:
        self._session_manager = session_manager

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self._session_manager.handle_request(scope, receive, send)


def _normalize_base_path(base_path: str | None, *, default: str = "/mcp") -> str:
    """Normalize base path ensuring a leading slash and no trailing slash (except root)."""
    if base_path is None:
        cleaned = default
    else:
        cleaned = base_path.strip() or default

    if not cleaned.startswith("/"):
        cleaned = f"/{cleaned}"

    if len(cleaned) > 1 and cleaned.endswith("/"):
        cleaned = cleaned.rstrip("/")

    return cleaned


def _build_route_variants(base_path: str) -> list[str]:
    """Return the set of route paths that should map to the transport."""
    variants = {base_path}
    if base_path != "/":
        if base_path.endswith("/"):
            variants.add(base_path.rstrip("/"))
        else:
            variants.add(f"{base_path}/")
    return sorted(variants)


def create_starlette_app(
    mcp_server: Server,
    *,
    debug: bool = False,
    base_path: str = "/mcp",
) -> Starlette:
    """Create a Starlette application exposing the MCP server over Streamable HTTP."""
    session_manager = StreamableHTTPSessionManager(mcp_server)
    streamable_http_app = _StreamableHTTPASGIApp(session_manager)

    normalized_path = _normalize_base_path(base_path)
    routes = [Route(path, endpoint=streamable_http_app) for path in _build_route_variants(normalized_path)]

    return Starlette(
        debug=debug,
        routes=routes,
        lifespan=lambda app: session_manager.run(),
    )


class ServiceNowSSEMCP(ServiceNowMCP):
    """ServiceNow MCP server exposed over the Streamable HTTP transport."""

    def __init__(self, config: Union[Dict, ServerConfig]):
        super().__init__(config)

    def start(self, host: str = "0.0.0.0", port: int = 8080) -> None:
        """Start the MCP server using the Streamable HTTP transport."""
        debug_enabled = bool(getattr(self.config, "debug", False))
        base_path = _normalize_base_path(os.getenv("SERVICENOW_HTTP_BASE_PATH"), default="/mcp")

        starlette_app = create_starlette_app(
            self.mcp_server,
            debug=debug_enabled,
            base_path=base_path,
        )

        display_path = base_path if base_path != "/" else "/"
        logger.info(
            "Serving ServiceNow MCP Streamable HTTP endpoints at %s (host=%s, port=%s)",
            display_path,
            host,
            port,
        )

        uvicorn.run(starlette_app, host=host, port=port)


def create_servicenow_mcp(instance_url: str, username: str, password: str) -> ServiceNowSSEMCP:
    """Factory for a ServiceNow MCP server instance with basic authentication."""
    auth_config = AuthConfig(
        type=AuthType.BASIC,
        basic=BasicAuthConfig(username=username, password=password),
    )
    config = ServerConfig(instance_url=instance_url, auth=auth_config)
    return ServiceNowSSEMCP(config)


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Run ServiceNow MCP server over Streamable HTTP",
    )
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    server = create_servicenow_mcp(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL"),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
    )
    server.start(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
