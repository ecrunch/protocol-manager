# Notion Python Client

A comprehensive Python client for the Notion API that provides access to all Notion API endpoints with proper error handling, rate limiting, and data validation.

## Features

- **Complete API Coverage**: Support for all Notion API endpoints (Pages, Blocks, Databases, Users, Search)
- **Type Safety**: Full type hints and Pydantic models for request/response validation
- **Rate Limiting**: Built-in rate limiting with exponential backoff retry logic
- **Authentication**: Support for both Integration Token and OAuth 2.0 authentication
- **Error Handling**: Comprehensive error handling with custom exception types
- **Async Support**: Optional async/await support for high-performance scenarios
- **Utilities**: Helper functions for creating common Notion objects and blocks
- **Pagination**: Automatic pagination handling for all list endpoints

## Installation

```bash
pip install -r requirements.txt
```

Or install with optional dependencies:

```bash
# For async support
pip install -e ".[async]"

# For CLI features  
pip install -e ".[cli]"

# For development
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
from notion_client import NotionClient

# Initialize with integration token
client = NotionClient(auth_token="secret_...")

# Or from environment variables
client = NotionClient.from_env()

# Test connection
if client.test_connection():
    print("Connected to Notion!")

# Search for pages
results = client.search.search_pages("My Project")

# Create a new page
page = client.pages.create(
    parent={"type": "page_id", "page_id": "parent_page_id"},
    properties={
        "title": {
            "title": [{"type": "text", "text": {"content": "New Page"}}]
        }
    }
)

# Add content to the page
from notion_client.utils import create_paragraph_block, create_heading_block

blocks = [
    create_heading_block("Welcome!", level=1),
    create_paragraph_block("This is my new page content.")
]

client.blocks.append_children(page.id, blocks)
```

### Environment Setup

Create a `.env` file (copy from `env.example`):

```env
NOTION_API_TOKEN=secret_your_integration_token_here
NOTION_API_VERSION=2022-06-28
```

### Database Operations

```python
# Query a database
database_pages = client.databases.query_all(
    database_id="database_id",
    filter_criteria={
        "property": "Status",
        "select": {"equals": "In Progress"}
    }
)

# Create a new database
database = client.databases.create(
    parent={"type": "page_id", "page_id": "parent_page_id"},
    title=[{"type": "text", "text": {"content": "My Database"}}],
    properties={
        "Name": {"title": {}},
        "Status": {
            "select": {
                "options": [
                    {"name": "Not Started", "color": "red"},
                    {"name": "In Progress", "color": "yellow"},
                    {"name": "Completed", "color": "green"}
                ]
            }
        }
    }
)
```

### Block Management

```python
# Get all blocks from a page
blocks = client.blocks.get_all_children("page_id")

# Create different types of blocks
from notion_client.utils import *

blocks_to_add = [
    create_heading_block("Section Title", level=2),
    create_paragraph_block("Some text content", bold=True),
    create_todo_block("Complete this task", checked=False),
    create_bulleted_list_item("First item"),
    create_numbered_list_item("Numbered item"),
    create_code_block("print('Hello World')", language="python"),
    create_quote_block("An inspiring quote"),
    create_callout_block("Important note", icon="💡"),
    create_divider_block(),
]

client.blocks.append_children("page_id", blocks_to_add)
```

## API Reference

### Client Initialization

```python
# Integration Token
client = NotionClient(auth_token="secret_...")

# OAuth (requires additional setup)
client = NotionClient.from_oauth(
    client_id="oauth_client_id",
    client_secret="oauth_client_secret", 
    redirect_uri="https://example.com/callback",
    access_token="access_token"  # optional
)

# From environment variables
client = NotionClient.from_env()
```

### Endpoints

The client provides access to all Notion API endpoints:

- `client.pages` - Page operations (create, retrieve, update, delete)
- `client.blocks` - Block operations (retrieve, update, delete, children)
- `client.databases` - Database operations (create, retrieve, update, query)
- `client.users` - User operations (list, retrieve)
- `client.search` - Search operations (pages, databases)

### Error Handling

```python
from notion_client.exceptions import (
    NotionAPIError,
    NotionAuthError,
    NotionRateLimitError,
    NotionValidationError,
    NotionConnectionError,
    NotionNotFoundError
)

try:
    page = client.pages.retrieve("invalid_id")
except NotionNotFoundError:
    print("Page not found")
except NotionAuthError:
    print("Authentication failed")
except NotionRateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except NotionAPIError as e:
    print(f"API error: {e.message}")
```

## Examples

See the `examples/` directory for complete usage examples:

- `basic_usage.py` - Basic operations and getting started
- `advanced_examples.py` - Advanced features and patterns
- `async_examples.py` - Async/await usage patterns

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd notion-client

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=notion_client

# Run integration tests (requires valid Notion token)
pytest -m integration
```

### Code Quality

```bash
# Format code
black notion_client/

# Sort imports
isort notion_client/

# Lint code
flake8 notion_client/

# Type checking
mypy notion_client/
```

## Configuration

### Environment Variables

- `NOTION_API_TOKEN` - Integration token for authentication
- `NOTION_API_VERSION` - API version (default: 2022-06-28)
- `NOTION_REQUEST_TIMEOUT` - Request timeout in seconds (default: 30)
- `NOTION_MAX_RETRIES` - Maximum retry attempts (default: 3)
- `NOTION_RATE_LIMIT_DELAY` - Rate limit delay (default: 1.0)

### OAuth Configuration

For OAuth authentication, additional environment variables:

- `NOTION_OAUTH_CLIENT_ID` - OAuth client ID
- `NOTION_OAUTH_CLIENT_SECRET` - OAuth client secret  
- `NOTION_OAUTH_REDIRECT_URI` - OAuth redirect URI
- `NOTION_OAUTH_ACCESS_TOKEN` - Current access token (optional)
- `NOTION_OAUTH_REFRESH_TOKEN` - Refresh token (optional)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Run code quality checks (`black`, `isort`, `flake8`, `mypy`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built according to the official [Notion API documentation](https://developers.notion.com/)
- Inspired by the official Notion SDK patterns
- Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- Built with [requests](https://docs.python-requests.org/) for HTTP client functionality
