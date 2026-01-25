# Troubleshooting Guide

This reference covers common issues and solutions when using OpenAI Agents SDK with Google Gemini.

## Authentication Issues

### Error: Invalid API Key

**Symptom**:
```
openai.AuthenticationError: Invalid API Key
```

**Solution**:
```python
import os

# Verify API key is set
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Check for common issues
if api_key.startswith("sk-"):
    raise ValueError("This looks like an OpenAI key, not a Gemini key")

print(f"API key length: {len(api_key)}")  # Should be ~39 characters
```

**Checklist**:
- [ ] `GEMINI_API_KEY` environment variable is set
- [ ] Key does not start with `sk-` (that's OpenAI)
- [ ] Key is from Google AI Studio (https://aistudio.google.com/apikey)
- [ ] Key has not expired or been revoked

### Error: 401 Unauthorized

**Symptom**:
```
httpx.HTTPStatusError: 401 Unauthorized
```

**Solution**:
```bash
# Regenerate API key from Google AI Studio
# https://aistudio.google.com/apikey

# Set new key
export GEMINI_API_KEY="your-new-api-key"
```

## API Endpoint Issues

### Error: 404 Not Found

**Symptom**:
```
openai.NotFoundError: Error code: 404
```

**Cause**: Using Responses API instead of Chat Completions

**Solution**:
```python
# WRONG - uses Responses API by default
from agents import Agent, Runner

agent = Agent(name="Test", model="gemini-2.5-flash")

# CORRECT - use OpenAIChatCompletionsModel
from agents import Agent, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

set_tracing_disabled(disabled=True)

gemini_model = OpenAIChatCompletionsModel(
    openai_client=AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    model="gemini-2.5-flash-preview-05-20"
)

agent = Agent(name="Test", model=gemini_model)
```

### Error: Invalid Base URL

**Symptom**:
```
httpx.ConnectError: Connection refused
```

**Solution**:
```python
# Correct base URL for Gemini
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

# Common mistakes:
# - Missing trailing slash
# - Wrong version (v1 instead of v1beta)
# - Typos in domain
```

## Model Issues

### Error: Model Not Found

**Symptom**:
```
openai.NotFoundError: The model `gemini-pro` does not exist
```

**Solution**:
```python
# Use correct model names
VALID_MODELS = [
    "gemini-2.5-flash-preview-05-20",  # Latest flash
    "gemini-2.5-pro-preview-05-06",    # Latest pro
    "gemini-2.0-flash",                # Stable flash
    "gemini-1.5-pro",                  # Legacy pro
    "gemini-1.5-flash",                # Legacy flash
]

# Avoid deprecated or invalid names:
# - "gemini-pro" (use full version)
# - "gemini-flash" (use full version)
# - "gpt-4" (OpenAI model, wrong SDK)
```

### Error: Model Overloaded

**Symptom**:
```
openai.RateLimitError: Model is overloaded
```

**Solution**:
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
async def run_with_retry(agent, input_text):
    return await Runner.run(agent, input=input_text)

# Or switch to a different model
FALLBACK_MODEL = "gemini-2.0-flash"  # More capacity
```

## Tracing Issues

### Error: Tracing Failed

**Symptom**:
```
agents.exceptions.TracingError: Failed to send trace
```

**Solution**:
```python
from agents import set_tracing_disabled

# ALWAYS disable tracing for Gemini
set_tracing_disabled(disabled=True)

# Or in RunConfig
from agents import RunConfig

config = RunConfig(tracing_disabled=True)
result = await Runner.run(agent, input="...", run_config=config)
```

## Tool Issues

### Error: Tool Schema Invalid

**Symptom**:
```
pydantic.ValidationError: Invalid tool schema
```

**Solution**:
```python
# WRONG - missing type hints
@function_tool
def bad_tool(data):
    return str(data)

# CORRECT - full type hints
@function_tool
def good_tool(data: str) -> str:
    """Process the data.

    Args:
        data: The input data to process.
    """
    return f"Processed: {data}"
```

### Error: Tool Not Called

**Symptom**: Agent ignores available tools

**Solution**:
```python
# 1. Check tool descriptions are clear
@function_tool
def search(query: str) -> str:
    """Search the web for information.  # Clear description

    Use this tool when you need to find current information
    that you don't already know.

    Args:
        query: The search query string.
    """
    return f"Results for: {query}"

# 2. Use tool_choice to force tool usage
from agents import ModelSettings

agent = Agent(
    name="Tool User",
    instructions="Use tools to answer questions.",
    model=gemini_model,
    tools=[search],
    model_settings=ModelSettings(tool_choice="required"),
)

# 3. Mention tools in instructions
instructions = """You are a research assistant.
ALWAYS use the search tool to find information.
Never make up facts - search first."""
```

### Error: Tool Timeout

**Symptom**: Tool execution hangs

**Solution**:
```python
import asyncio
from agents import function_tool

@function_tool
async def safe_api_call(endpoint: str) -> str:
    """Call an API with timeout protection.

    Args:
        endpoint: The API endpoint to call.
    """
    try:
        async with asyncio.timeout(30):  # 30 second timeout
            # Your API call here
            result = await fetch_api(endpoint)
            return result
    except asyncio.TimeoutError:
        return "Error: API call timed out"
```

## Handoff Issues

### Error: Handoff Not Triggered

**Symptom**: Agent doesn't hand off when expected

**Solution**:
```python
# 1. Make handoff criteria explicit in instructions
instructions = """You are a triage agent.

IMMEDIATELY hand off to Sales Agent when user mentions:
- pricing
- purchase
- buy
- cost

IMMEDIATELY hand off to Support Agent when user mentions:
- error
- bug
- broken
- not working

Do NOT try to answer these questions yourself."""

# 2. Use descriptive handoff tool names
from agents import handoff

handoffs = [
    handoff(
        sales_agent,
        tool_name="transfer_to_sales",
        tool_description="Use this to transfer pricing and purchase questions to sales"
    ),
]
```

### Error: Lost Context in Handoff

**Symptom**: New agent doesn't know conversation history

**Solution**:
```python
from agents import RunConfig

config = RunConfig(
    # Preserve history during handoff
    nest_handoff_history=True,
)

result = await Runner.run(
    triage_agent,
    input="...",
    run_config=config,
)
```

## Performance Issues

### Slow Response Times

**Solution**:
```python
# 1. Use streaming for perceived speed
result = Runner.run_streamed(agent, input="...")
async for event in result.stream_events():
    if hasattr(event, 'delta'):
        print(event.delta, end='', flush=True)

# 2. Use faster model
model = "gemini-2.5-flash-preview-05-20"  # Faster than pro

# 3. Reduce max_tokens
settings = ModelSettings(max_tokens=500)  # Limit response length

# 4. Limit turns
config = RunConfig(max_turns=5)  # Prevent runaway conversations
```

### Memory Issues

**Solution**:
```python
# 1. Limit conversation history
from agents import RunConfig

config = RunConfig(
    # Custom history handling
    call_model_input_filter=lambda agent, ctx, data: trim_history(data, max_items=20)
)

# 2. Clear unused references
agent = None  # Allow garbage collection
```

## Debugging Tips

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("agents").setLevel(logging.DEBUG)
logging.getLogger("openai").setLevel(logging.DEBUG)
```

### Inspect API Calls

```python
from openai import AsyncOpenAI

class DebugClient(AsyncOpenAI):
    async def _request(self, *args, **kwargs):
        print(f"Request: {args}, {kwargs}")
        response = await super()._request(*args, **kwargs)
        print(f"Response: {response}")
        return response

debug_client = DebugClient(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=os.getenv("GEMINI_API_KEY"),
)
```

### Test Model Connection

```python
async def test_connection():
    """Quick test to verify Gemini connection works."""
    from agents import Agent, Runner, set_tracing_disabled
    from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
    from openai import AsyncOpenAI

    set_tracing_disabled(disabled=True)

    model = OpenAIChatCompletionsModel(
        openai_client=AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("GEMINI_API_KEY"),
        ),
        model="gemini-2.5-flash-preview-05-20"
    )

    agent = Agent(name="Test", instructions="Say hello", model=model)

    try:
        result = await Runner.run(agent, input="Hi")
        print(f"SUCCESS: {result.final_output}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")

# Run test
import asyncio
asyncio.run(test_connection())
```
