# sensorbio-mcp-server (Python)

Python MCP (Model Context Protocol) server for **Sensor Bio** (https://api.sensorbio.com).

## Requirements
- Python **3.11+**
- `uv` / `uvx`

## Authentication

This server supports **two** authentication modes:

### 1) Organization token (recommended if you have it)

- Env var: `SENSR_ORG_TOKEN` (preferred) or `SENSR_API_KEY` (alias)
- Request header: `Authorization: APIKey <token>`

### 2) OAuth2 (client_credentials)

- Env vars: `SENSR_CLIENT_ID`, `SENSR_CLIENT_SECRET`
- Optional: `SENSR_SCOPE`
- Token URL: `https://auth.sensorbio.com/token`
- (Documented, not used for client_credentials) Auth URL: `https://auth.sensorbio.com/authorize`
- (Documented) Redirect URL: `https://developers.sensorbio.com/`

Notes:
- `SensrClient.from_env()` uses `SENSR_ORG_TOKEN` first, then falls back to `SENSR_API_KEY`. If neither is present, it uses OAuth.
- OAuth access tokens are cached in-memory and refreshed when there are **< 60s** left before expiry.

## Install / Run (uvx)

### From local checkout
```bash
uvx --from . sensorbio-mcp-server
```

### From GitHub
```bash
uvx --from git+https://github.com/GetSensr-io/sensorbio-mcp-server sensorbio-mcp-server
```

## Claude Desktop config

Add this to Claude Desktop `mcpServers`.

### Option A: Organization token
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
        "SENSR_ORG_TOKEN": "YOUR_SENSR_ORG_TOKEN"
      }
    }
  }
}
```

### Option B: OAuth2 client_credentials
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
        "SENSR_CLIENT_ID": "YOUR_CLIENT_ID",
        "SENSR_CLIENT_SECRET": "YOUR_CLIENT_SECRET",
        "SENSR_SCOPE": "optional"
      }
    }
  }
}
```

## Tools exposed
- `list_users(page=1, limit=100, search=None)`
- `get_user_ids()`
- `get_user_by_email(email)`
- `search_user(query, page=1, limit=50)`
- `get_sleep(user_id, date=None, start_date=None, end_date=None, days=None, summary_only=True)`
- `get_scores(user_id, date=None, start_date=None, end_date=None, days=None)`
- `get_activities(user_id, start_date=None, end_date=None, start_timestamp_ms=None, end_timestamp_ms=None, cursor=None, last_timestamp=None, limit=50)`
- `get_biometrics(user_id, start_date=None, end_date=None, start_timestamp_ms=None, end_timestamp_ms=None, cursor=None, last_timestamp=None, limit=50)`
- `get_calories(user_id, date=None, start_date=None, end_date=None, days=None, granularity=None)`
- `get_org_sleep_summary(date=None, start_date=None, end_date=None, days=None)`
- `get_org_scores_summary(date=None, start_date=None, end_date=None, days=None)`
- `debug_request(path, query=None)`

## Smoke test

Calls `/v1/organizations/users/ids` using the active auth mode:

```bash
uv run python3 scripts/smoke_test.py
```

