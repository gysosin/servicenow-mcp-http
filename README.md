# ServiceNow MCP Server

ServiceNow MCP Server implements the Model Context Protocol (MCP) so Claude and other MCP-compatible clients can safely interact with a ServiceNow instance. The server translates tool calls coming from the client into ServiceNow REST API requests and returns structured results that are easy for language models to use.

## Highlights
- Multiple authentication flows: basic auth, OAuth, and API key exchange
- Rich catalogue of tools for incidents, catalog items, workflows, changesets, knowledge, and agile work
- Selective tool loading through role-focused packages to stay within model limits
- Supports both standard input/output transports and a Streamable HTTP endpoint
- Ships with runnable examples, scripted setup helpers, and an automated pytest suite

## Repository Layout
- `src/servicenow_mcp/` core server implementation, CLI entry points, tool definitions, and utilities
- `config/tool_packages.yaml` default role-based tool bundles that can be tuned for your organisation
- `docs/` feature deep dives and operational guidance for catalog, workflow, change, and user management
- `examples/` runnable scripts that demonstrate common flows and integration patterns
- `scripts/` helper commands for configuring credentials, checking instance status, and other local tasks
- `tests/` pytest coverage for key tools, resources, and transports

## Getting Started
### Requirements
- Python 3.11+
- ServiceNow instance credentials with the permissions required by the tools you plan to expose

### Clone and Install
```bash
git clone https://github.com/gysosin/servicenow-mcp-http.git
cd servicenow-mcp-http
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

Copy the example environment file and fill in the placeholders:
```bash
cp .env.example .env
```

## Configuration
### Core Environment Variables
- `SERVICENOW_INSTANCE_URL` e.g. `https://your-instance.service-now.com`
- `SERVICENOW_AUTH_TYPE` one of `basic`, `oauth`, or `api_key`
- `SERVICENOW_USERNAME` and `SERVICENOW_PASSWORD` for basic auth
- `SERVICENOW_API_KEY` when using the API key flow
- `SERVICENOW_CLIENT_ID`, `SERVICENOW_CLIENT_SECRET`, and `SERVICENOW_TOKEN_URL` for OAuth
- `SERVICENOW_HTTP_HOST`, `SERVICENOW_HTTP_PORT`, and `SERVICENOW_HTTP_BASE_PATH` to adjust the optional HTTP transport

All environment variables can be added to the `.env` file for local development; the CLI loads that file automatically.

## Running the Server
### Standard MCP (stdio) Transport
Launch the server directly from Python or the installed console script:
```bash
python -m servicenow_mcp.cli
# or
servicenow-mcp
```

Pass credentials inline if you prefer not to use a `.env` file:
```bash
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com \
SERVICENOW_USERNAME=your-username \
SERVICENOW_PASSWORD=your-password \
SERVICENOW_AUTH_TYPE=basic \
servicenow-mcp
```

### Streamable HTTP Transport
Expose the server over HTTP for clients that speak the MCP Streamable specification:
```bash
servicenow-mcp-sse --instance-url https://your-instance.service-now.com \
  --auth-type basic --username your-username --password your-password \
  --host 0.0.0.0 --port 8080
```

The HTTP application exposes `POST /mcp` for JSON-RPC messages and `GET /mcp` for the event stream. Adjust the base path with `SERVICENOW_HTTP_BASE_PATH` if you need to serve the API from a different route.

## Tool Packages
The server can limit which tools are registered by setting `MCP_TOOL_PACKAGE`. Packages are defined in `config/tool_packages.yaml` and can be customised to fit your deployment. Useful defaults include:
- `service_desk` incidents, user lookup, and knowledge retrieval
- `catalog_builder` catalog items, categories, variables, and optimisation helpers
- `change_coordinator` change requests, approvals, and related tasks
- `knowledge_author` knowledge base, category, and article lifecycle management
- `platform_developer` script includes, workflows, and changeset operations
- `system_administrator` user and group management plus syslog access
- `agile_management` epics, stories, scrum tasks, and project resources
- `full` enables every tool (default)
- `none` disables all tools except the introspection helper

Switch packages per run:
```bash
export MCP_TOOL_PACKAGE=catalog_builder
servicenow-mcp
```

The `list_tool_packages` tool is always available (except when `none` is selected) to report which package is active.

## Examples and Documentation
- Browse the `examples/` directory for scripts that exercise catalog optimisation, change management, workflow automation, and more.
- The `docs/` folder contains detailed guidance for catalog, change, workflow, knowledge, and user management features.
- `debug_workflow_api.py` and `examples/debug_workflow_api.py` show how to introspect workflow definitions interactively.

## Development Workflow
```bash
pip install -e .[dev]
pytest
ruff check src tests
black src tests
```

Use the scripts in `scripts/` to validate ServiceNow credentials and wake developer instances before running the server.

## Troubleshooting
- `argument after ** must be a mapping`: pass dictionaries to change-management helpers instead of Pydantic models; the helpers attempt to unwrap invalid inputs automatically.
- `Missing required parameter 'type'`: ensure required ServiceNow fields (such as `short_description` and `type` when creating change requests) are supplied.
- `Invalid value for parameter 'type'`: use accepted ServiceNow enumerations (`normal`, `standard`, `emergency`, etc.).
- `Cannot find get_headers method`: confirm tool arguments are provided in the correct order so the auth manager is passed first.

## Contributing
Pull requests are welcome. Please fork the repository, create a feature branch, and open a PR once tests pass locally.

## License
Released under the MIT License. See `LICENSE` for details.
