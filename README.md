# Sensor Bio MCP Server

[![CI](https://github.com/GetSensr-io/sensorbio-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/GetSensr-io/sensorbio-mcp-server/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Connect your Sensor Bio wearable data to Claude, ChatGPT, and other AI assistants using the [Model Context Protocol (MCP)](https://modelcontextprotocol.io/).

Ask your AI assistant things like *"How did I sleep last week?"*, *"What's my resting heart rate trend?"*, or *"Show me my recovery scores for the past month"* and get answers pulled directly from your Sensor Bio data.

---

## Quick Start

### 1. Get your API token

Log in to your [Sensor Bio developer portal](https://developers.sensorbio.com/) and grab your **Organization API Token**.

### 2. Install uv

This server uses [uv](https://docs.astral.sh/uv/getting-started/installation/) to run. Install it with one command:

**Mac / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 3. Add to Claude Desktop

Open your Claude Desktop config file:

| OS      | Path                                                              |
| ------- | ----------------------------------------------------------------- |
| macOS   | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json`                     |
| Linux   | `~/.config/Claude/claude_desktop_config.json`                     |

Add (or merge into) the `mcpServers` section:

```json
{
  "mcpServers": {
    "sensorbio": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/GetSensr-io/sensorbio-mcp-server",
        "sensorbio-mcp-server"
      ],
      "env": {
        "SENSR_ORG_TOKEN": "paste-your-token-here"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

Quit and reopen Claude Desktop. You should see "sensorbio" in the MCP tools list (look for the hammer icon).

### 5. Try it out

Ask Claude something like:

> "Show me my sleep data from the past week"

> "How many calories did I burn yesterday?"

> "List all users in my organization"

---

## Other MCP Clients

### Cursor / Windsurf

These editors support MCP servers natively. Use the same config format above in their respective MCP settings.

### OpenAI (ChatGPT)

MCP support in ChatGPT is rolling out. When available, the same server and config pattern will work.

### Any MCP Client

Any application that supports the [Model Context Protocol](https://modelcontextprotocol.io/) can connect using this server. Just point it at:

```
uvx --from git+https://github.com/GetSensr-io/sensorbio-mcp-server sensorbio-mcp-server
```

---

## Authentication

| Method              | Env Vars                                      | Best For                    |
| ------------------- | --------------------------------------------- | --------------------------- |
| **API Token**       | `SENSR_ORG_TOKEN` or `SENSR_API_KEY`          | Most users (recommended)    |
| **OAuth2**          | `SENSR_CLIENT_ID` + `SENSR_CLIENT_SECRET`     | Programmatic / advanced use |

The server checks for `SENSR_ORG_TOKEN` first, then `SENSR_API_KEY` as a fallback. If neither is set, it tries OAuth2 client credentials.

### OAuth2 Config (advanced)

```json
{
  "mcpServers": {
    "sensorbio": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/GetSensr-io/sensorbio-mcp-server",
        "sensorbio-mcp-server"
      ],
      "env": {
        "SENSR_CLIENT_ID": "your-client-id",
        "SENSR_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

---

## What You Can Ask

Once connected, your AI assistant has access to these tools:

| Tool                       | What it does                                           | Example question                                  |
| -------------------------- | ------------------------------------------------------ | ------------------------------------------------- |
| **list_users**             | List all users in your organization                    | "Show me all users"                               |
| **get_user_ids**           | Get all user IDs                                       | "How many users are in the org?"                  |
| **get_user_by_email**      | Find a user by their email address                     | "Look up john@example.com"                        |
| **get_user_profile**       | Get a specific user's full profile                     | "Show me Bryan's profile"                         |
| **search_user**            | Search users by name or email                          | "Find users named Sarah"                          |
| **get_sleep**              | Sleep data: duration, score, stages                    | "How did I sleep last week?"                      |
| **get_scores**             | Recovery, sleep, and activity scores                   | "What's my recovery score today?"                 |
| **get_activities**         | Workouts and activity sessions                         | "What workouts did I do this week?"               |
| **get_biometrics**         | Heart rate, HRV, SpO2, respiratory rate                | "What's my resting heart rate?"                   |
| **get_calories**           | Calorie burn details                                   | "How many calories did I burn today?"             |
| **get_org_sleep_summary**  | Sleep overview across your whole org                   | "How did the team sleep last night?"              |
| **get_org_scores_summary** | Score overview across your whole org                   | "Show me the team's recovery scores"              |
| **debug_request**          | Raw API request (for troubleshooting)                  | Usually not needed directly                       |

Most tools support flexible date ranges. You can say things like "last 7 days", "March 1st to March 10th", or "yesterday" and the AI will figure out the right parameters.

---

## Environment Variables

| Variable              | Required | Description                                                      |
| --------------------- | -------- | ---------------------------------------------------------------- |
| `SENSR_ORG_TOKEN`     | *        | Organization API token (recommended)                             |
| `SENSR_API_KEY`       | *        | Alias for `SENSR_ORG_TOKEN`                                      |
| `SENSR_CLIENT_ID`     | **       | OAuth2 client ID                                                 |
| `SENSR_CLIENT_SECRET` | **       | OAuth2 client secret                                             |
| `SENSR_SCOPE`         |          | OAuth2 scope (optional)                                          |
| `SENSR_BASE_URL`      |          | Override API base URL (default: `https://api.sensorbio.com`)     |
| `SENSR_TZ`            |          | Timezone for "today" calculations (default: `America/Chicago`)   |

\* Set one of `SENSR_ORG_TOKEN` or `SENSR_API_KEY` for token auth.
\*\* Set both for OAuth2 auth. Token auth takes precedence if both are configured.

---

## Troubleshooting

**"Server not connecting"**
- Make sure `uv` is installed: run `uv --version` in your terminal
- Check that your config file path is correct (see table above)
- Make sure you restarted Claude Desktop after editing the config

**"Authentication error" or "Invalid API Key"**
- Double-check your token. Copy it fresh from the developer portal.
- Make sure there are no extra spaces or line breaks in the token
- Tokens can expire. Generate a new one if yours is old.

**"No data showing"**
- Your Sensor Bio device needs to have synced recently
- Check that the user ID exists in your organization
- Try asking for a specific date: "Show my sleep for March 10th"

**"Tool not found"**
- Make sure the MCP server name in your config is exactly `sensorbio`
- Check Claude Desktop's MCP tools list for connection status

---

## Development

Want to contribute or run locally?

```bash
# Clone the repo
git clone https://github.com/GetSensr-io/sensorbio-mcp-server.git
cd sensorbio-mcp-server

# Install dependencies
uv sync --dev

# Run tests
uv run pytest -v

# Lint
uv run ruff check .

# Run the server locally
SENSR_ORG_TOKEN=your-token uvx --from . sensorbio-mcp-server

# Smoke test (needs a valid token)
SENSR_ORG_TOKEN=your-token uv run python scripts/smoke_test.py
```

---

## License

MIT
