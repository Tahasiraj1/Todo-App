# Tool Creation Patterns

This reference covers creating and using tools with the OpenAI Agents SDK.

## @function_tool Decorator

The `@function_tool` decorator converts Python functions into agent tools.

### Basic Tool

```python
from agents import function_tool

@function_tool
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b
```

### Async Tool

```python
from agents import function_tool
import httpx

@function_tool
async def fetch_data(url: str) -> str:
    """Fetch data from a URL.

    Args:
        url: The URL to fetch data from.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
```

### Tool with Context

```python
from agents import function_tool, RunContextWrapper

@function_tool
def get_user_info(ctx: RunContextWrapper) -> str:
    """Get the current user's information."""
    user_id = ctx.context.get("user_id")
    return f"User ID: {user_id}"
```

### Tool with Typed Context

```python
from agents import function_tool, RunContextWrapper
from dataclasses import dataclass

@dataclass
class AppContext:
    user_id: str
    session_token: str
    permissions: list[str]

@function_tool
def check_permission(ctx: RunContextWrapper[AppContext], permission: str) -> bool:
    """Check if user has a specific permission.

    Args:
        permission: The permission to check.
    """
    return permission in ctx.context.permissions
```

## Decorator Options

### Custom Name

```python
@function_tool(name_override="search")
def search_database(query: str) -> str:
    """Search the database."""
    return f"Results for: {query}"
```

### Custom Description

```python
@function_tool(description_override="Performs a web search and returns results")
def web_search(query: str) -> str:
    """Internal search function."""
    return f"Search results for: {query}"
```

### Strict Mode

```python
# Strict mode (default) - enforces JSON schema validation
@function_tool(strict_mode=True)
def strict_tool(value: int) -> int:
    """Process a value."""
    return value * 2

# Non-strict mode - allows optional parameters
@function_tool(strict_mode=False)
def flexible_tool(required: str, optional: str = "default") -> str:
    """Process with optional parameter."""
    return f"{required} - {optional}"
```

### Conditional Enablement

```python
from agents import function_tool, RunContextWrapper, AgentBase

def is_admin(ctx: RunContextWrapper, agent: AgentBase) -> bool:
    return ctx.context.get("is_admin", False)

@function_tool(is_enabled=is_admin)
def admin_only_tool() -> str:
    """Only available to admin users."""
    return "Admin action performed"
```

### Custom Error Handling

```python
from agents import function_tool, ToolContext

def handle_error(error: Exception, ctx: ToolContext, input_str: str) -> str:
    return f"Tool failed: {str(error)}. Please try again."

@function_tool(failure_error_function=handle_error)
def risky_operation(data: str) -> str:
    """Perform a risky operation."""
    if not data:
        raise ValueError("Data cannot be empty")
    return f"Processed: {data}"
```

## Complex Parameter Types

### TypedDict Parameters

```python
from typing import TypedDict
from agents import function_tool

class Location(TypedDict):
    latitude: float
    longitude: float
    name: str

@function_tool
def get_weather(location: Location) -> str:
    """Get weather for a location.

    Args:
        location: The location with lat, long, and name.
    """
    return f"Weather at {location['name']}: Sunny, 72°F"
```

### List Parameters

```python
from agents import function_tool

@function_tool
def process_items(items: list[str]) -> str:
    """Process a list of items.

    Args:
        items: List of item names to process.
    """
    return f"Processed {len(items)} items: {', '.join(items)}"
```

### Optional Parameters

```python
from agents import function_tool

@function_tool(strict_mode=False)  # Required for optional params
def search(
    query: str,
    limit: int = 10,
    include_metadata: bool = False
) -> str:
    """Search with optional parameters.

    Args:
        query: The search query.
        limit: Maximum results (default: 10).
        include_metadata: Include metadata in results.
    """
    return f"Searching '{query}' with limit={limit}, metadata={include_metadata}"
```

### Enum Parameters

```python
from enum import Enum
from agents import function_tool

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@function_tool
def create_task(title: str, priority: Priority) -> str:
    """Create a task with priority.

    Args:
        title: The task title.
        priority: Task priority level.
    """
    return f"Created task '{title}' with {priority.value} priority"
```

## Attaching Tools to Agents

```python
from agents import Agent

# Single tool
agent = Agent(
    name="Calculator",
    instructions="Help with calculations.",
    model=gemini_model,
    tools=[calculate_sum],
)

# Multiple tools
agent = Agent(
    name="Research Assistant",
    instructions="Help with research tasks.",
    model=gemini_model,
    tools=[
        web_search,
        fetch_data,
        calculate_sum,
        process_items,
    ],
)
```

## Tool Choice Configuration

```python
from agents import Agent, ModelSettings

# Auto (default) - model decides when to use tools
agent = Agent(
    name="Auto Tools",
    model=gemini_model,
    tools=[search, calculate],
    model_settings=ModelSettings(tool_choice="auto"),
)

# Required - model must use a tool
agent = Agent(
    name="Required Tools",
    model=gemini_model,
    tools=[search, calculate],
    model_settings=ModelSettings(tool_choice="required"),
)

# None - model cannot use tools
agent = Agent(
    name="No Tools",
    model=gemini_model,
    tools=[search, calculate],
    model_settings=ModelSettings(tool_choice="none"),
)

# Specific tool - force specific tool usage
agent = Agent(
    name="Specific Tool",
    model=gemini_model,
    tools=[search, calculate],
    model_settings=ModelSettings(tool_choice={"type": "function", "function": {"name": "search"}}),
)
```

## Tool Best Practices

### 1. Clear Docstrings

```python
# Good - clear description and arg documentation
@function_tool
def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email to a recipient.

    This tool sends an email using the configured SMTP server.
    Returns a confirmation message on success.

    Args:
        recipient: The email address of the recipient.
        subject: The subject line of the email.
        body: The main content of the email.
    """
    # Implementation
    return "Email sent successfully"

# Avoid - vague description
@function_tool
def do_email(to: str, sub: str, msg: str) -> str:
    """Send email."""
    return "done"
```

### 2. Type Annotations

```python
# Good - fully typed
@function_tool
def process_order(
    order_id: str,
    quantity: int,
    discount: float
) -> dict[str, any]:
    """Process an order."""
    return {"status": "processed", "order_id": order_id}

# Avoid - missing types
@function_tool
def process(data):
    """Process something."""
    return data
```

### 3. Error Handling

```python
@function_tool
def read_file(path: str) -> str:
    """Read contents of a file.

    Args:
        path: Path to the file to read.
    """
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {path}"
    except PermissionError:
        return f"Error: Permission denied for {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"
```

### 4. Validate Input

```python
@function_tool
def transfer_funds(
    from_account: str,
    to_account: str,
    amount: float
) -> str:
    """Transfer funds between accounts.

    Args:
        from_account: Source account ID.
        to_account: Destination account ID.
        amount: Amount to transfer.
    """
    # Validate input
    if amount <= 0:
        return "Error: Amount must be positive"
    if from_account == to_account:
        return "Error: Cannot transfer to same account"

    # Process transfer
    return f"Transferred ${amount} from {from_account} to {to_account}"
```
