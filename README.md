[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/taxuspt-garmin-mcp-badge.png)](https://mseep.ai/app/taxuspt-garmin-mcp)

# Garmin MCP Server

This Model Context Protocol (MCP) server connects to Garmin Connect and exposes your fitness and health data to Claude and other MCP-compatible clients.

## Features

- List recent activities
- Get detailed activity information
- Access health metrics (steps, heart rate, sleep)
- View body composition data

## Setup

### Local Development

1. Install the required packages on a new environment:

```bash
uv sync
```

### Docker

1. Copy the environment template and fill in your credentials:

```bash
cp .env.example .env
# Edit .env with your Garmin Connect credentials
```

2. Build the Docker image:

```bash
docker build -t garmin-mcp .
```

3. Run with environment variables:

```bash
docker run -e GARMIN_EMAIL=your@email.com -e GARMIN_PASSWORD=yourpassword garmin-mcp
```

4. Or use docker-compose for different modes:

```bash
# stdio mode (default)
docker-compose --profile stdio up

# SSE mode
docker-compose --profile sse up

# HTTP mode
docker-compose --profile http up
```

### Docker Volumes

The Docker setup includes a persistent volume for Garmin authentication tokens, so you won't need to re-authenticate every time you restart the container:

```bash
# View the volume
docker volume ls | grep garmin

# Inspect the volume
docker volume inspect garmin_mcp_garmin-tokens
```

## Environment Variables

The server supports the following environment variables:

- `GARMIN_EMAIL`: Your Garmin Connect email address (required)
- `GARMIN_PASSWORD`: Your Garmin Connect password (required)
- `GARMINTOKENS`: Path to store authentication tokens (default: `~/.garminconnect`)
- `GARMINTOKENS_BASE64`: Path to store base64-encoded tokens (default: `~/.garminconnect_base64`)
- `MCP_MODE`: Server transport mode - `stdio` (default), `sse`, or `http`
- `MCP_HOST`: Host address for sse/http modes (default: `127.0.0.1`)
- `MCP_PORT`: Port number for sse/http modes (default: `8080`)

### Server Modes

The server can run in three different modes:

1. **stdio** (default): Standard input/output communication, suitable for local development
2. **sse**: Server-Sent Events mode for web-based clients
3. **http**: HTTP streamable mode for remote connections

## Running the Server

### With Claude Desktop

1. Create a configuration in Claude Desktop:

Edit your Claude Desktop configuration file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add this server configuration:

```json
{
  "mcpServers": {
    "garmin": {
      "command": "uvx",
      "args": [
        "--python",
        "3.12",
        "--from",
        "git+https://github.com/Taxuspt/garmin_mcp",
        "garmin-mcp"
      ],
      "env": {
        "GARMIN_EMAIL": "YOUR_GARMIN_EMAIL",
        "GARMIN_PASSWORD": "YOUR_GARMIN_PASSWORD"
      }
    }
  }
}
```

Replace the path with the absolute path to your server file.

2. Restart Claude Desktop

### With MCP Inspector

For testing, you can use the MCP Inspector from the project root:

```bash
npx @modelcontextprotocol/inspector uv run garmin-mcp
```

### Different Server Modes

#### stdio Mode (Default)
```bash
# Run in stdio mode (default)
uv run garmin-mcp

# Or explicitly set the mode
MCP_MODE=stdio uv run garmin-mcp
```

#### SSE Mode
```bash
# Run in Server-Sent Events mode
MCP_MODE=sse MCP_HOST=0.0.0.0 MCP_PORT=8080 uv run garmin-mcp
```

#### HTTP Streamable Mode
```bash
# Run in HTTP streamable mode
MCP_MODE=http MCP_HOST=0.0.0.0 MCP_PORT=8080 uv run garmin-mcp
```


## Usage Examples

Once connected in Claude, you can ask questions like:

- "Show me my recent activities"
- "What was my sleep like last night?"
- "How many steps did I take yesterday?"
- "Show me the details of my latest run"

## Security Note

## Troubleshooting

If you encounter login issues:

1. Verify your credentials are correct
2. Check if Garmin Connect requires additional verification
3. Ensure the garminconnect package is up to date

For other issues, check the Claude Desktop logs at:

- macOS: `~/Library/Logs/Claude/mcp-server-garmin.log`
- Windows: `%APPDATA%\Claude\logs\mcp-server-garmin.log`
