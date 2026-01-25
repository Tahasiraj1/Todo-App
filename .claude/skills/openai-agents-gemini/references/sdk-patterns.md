# OpenAI Agents SDK Core Patterns

This reference covers the core patterns of the OpenAI Agents SDK when used with Google Gemini models.

## Agent Class

The `Agent` class is the core building block for creating AI agents.

### Basic Agent Definition

```python
from agents import Agent

agent = Agent(
    name="My Agent",
    instructions="You are a helpful assistant.",
    model=gemini_model,  # Always pass Gemini model
)
```

### Agent Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Unique identifier for the agent |
| `instructions` | `str` or `Callable` | System prompt or dynamic instruction function |
| `model` | `Model` | The Gemini model instance |
| `tools` | `list[Tool]` | List of tools the agent can use |
| `handoffs` | `list[Agent]` | Agents this agent can hand off to |
| `model_settings` | `ModelSettings` | Temperature, max_tokens, etc. |
| `output_type` | `Type` | Pydantic model for structured output |

### Dynamic Instructions

```python
from agents import Agent, RunContextWrapper

def get_instructions(context: RunContextWrapper) -> str:
    user_name = context.context.get("user_name", "User")
    return f"You are helping {user_name}. Be friendly and helpful."

agent = Agent(
    name="Dynamic Agent",
    instructions=get_instructions,
    model=gemini_model,
)
```

## Runner Class

The `Runner` executes agents and manages the conversation loop.

### Synchronous Execution

```python
from agents import Runner
import asyncio

async def main():
    result = await Runner.run(
        starting_agent=agent,
        input="Hello!",
    )
    print(result.final_output)

asyncio.run(main())
```

### Runner.run Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `starting_agent` | `Agent` | The initial agent to run |
| `input` | `str` or `list` | User input or conversation history |
| `context` | `Any` | Custom context passed to tools/instructions |
| `run_config` | `RunConfig` | Advanced configuration options |
| `max_turns` | `int` | Maximum conversation turns (default: 10) |
| `hooks` | `list[Hook]` | Lifecycle hooks for monitoring |

### Streamed Execution

```python
from agents import Runner

async def main():
    result = Runner.run_streamed(
        starting_agent=agent,
        input="Tell me a story",
    )

    async for event in result.stream_events():
        # Handle different event types
        print(event)

    # Get final output after streaming
    final_output = await result.final_output
```

## RunConfig

Configure advanced run settings.

```python
from agents import RunConfig, ModelSettings

config = RunConfig(
    # Override model for all agents in run
    model=gemini_model,

    # Global model settings
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=2000,
    ),

    # Maximum turns before stopping
    max_turns=15,

    # Disable tracing (required for Gemini)
    tracing_disabled=True,

    # Workflow name for debugging
    workflow_name="Customer Support",
)

result = await Runner.run(agent, input="Hi", run_config=config)
```

## ModelSettings

Fine-tune model behavior.

```python
from agents import ModelSettings

settings = ModelSettings(
    # Creativity level (0.0 to 2.0)
    temperature=0.7,

    # Maximum response tokens
    max_tokens=2000,

    # Tool choice behavior
    tool_choice="auto",  # "auto", "required", "none", or specific tool

    # Top-p sampling
    top_p=0.9,

    # Frequency penalty
    frequency_penalty=0.0,

    # Presence penalty
    presence_penalty=0.0,
)

agent = Agent(
    name="Configured Agent",
    instructions="...",
    model=gemini_model,
    model_settings=settings,
)
```

## Result Objects

### RunResult

```python
result = await Runner.run(agent, input="Hello")

# Access final output
print(result.final_output)

# Get the last agent that responded
print(result.last_agent.name)

# Access conversation history
for item in result.new_items:
    print(item)

# Check if handoff occurred
if result.last_agent != agent:
    print("Handoff occurred!")
```

### RunResultStreaming

```python
result = Runner.run_streamed(agent, input="Hello")

# Stream events
async for event in result.stream_events():
    # AgentUpdatedStreamEvent - agent changed
    # TextDeltaStreamEvent - text chunk
    # ToolCallStreamEvent - tool being called
    # etc.
    pass

# Current agent during streaming
current = result.current_agent

# Final output (blocks until complete)
final = await result.final_output
```

## Context Management

Pass custom context to agents and tools.

```python
from agents import Agent, Runner, function_tool, RunContextWrapper
from dataclasses import dataclass

@dataclass
class UserContext:
    user_id: str
    preferences: dict

@function_tool
def get_user_data(ctx: RunContextWrapper[UserContext]) -> str:
    """Get current user's data."""
    user_id = ctx.context.user_id
    return f"User ID: {user_id}"

agent = Agent(
    name="Context-Aware Agent",
    instructions="Help the user with their account.",
    model=gemini_model,
    tools=[get_user_data],
)

async def main():
    context = UserContext(user_id="123", preferences={"theme": "dark"})
    result = await Runner.run(
        agent,
        input="Show my user data",
        context=context,
    )
```

## Structured Output

Get typed responses using Pydantic models.

```python
from pydantic import BaseModel
from agents import Agent, Runner

class WeatherReport(BaseModel):
    city: str
    temperature: float
    condition: str
    humidity: int

agent = Agent(
    name="Weather Agent",
    instructions="Provide weather information in the specified format.",
    model=gemini_model,
    output_type=WeatherReport,
)

async def main():
    result = await Runner.run(
        agent,
        input="What's the weather in Tokyo?",
    )

    # result.final_output is a WeatherReport instance
    report: WeatherReport = result.final_output
    print(f"{report.city}: {report.temperature}°F, {report.condition}")
```

## Error Handling

```python
from agents import Runner
from agents.exceptions import MaxTurnsExceeded, AgentError

async def main():
    try:
        result = await Runner.run(
            agent,
            input="Complex task...",
            max_turns=5,
        )
    except MaxTurnsExceeded:
        print("Agent exceeded maximum turns")
    except AgentError as e:
        print(f"Agent error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

## Best Practices

### 1. Always Disable Tracing for Gemini

```python
from agents import set_tracing_disabled
set_tracing_disabled(disabled=True)
```

### 2. Reuse Model Instances

```python
# Good: Create once, reuse
gemini_model = create_gemini_model()
agent1 = Agent(name="Agent1", model=gemini_model, ...)
agent2 = Agent(name="Agent2", model=gemini_model, ...)

# Avoid: Creating new instances unnecessarily
```

### 3. Use Meaningful Agent Names

```python
# Good
agent = Agent(name="Customer Support Triage", ...)

# Avoid
agent = Agent(name="agent1", ...)
```

### 4. Clear Instructions

```python
# Good
instructions = """You are a customer support agent.
Your responsibilities:
1. Answer product questions
2. Help with order issues
3. Hand off complex billing to Billing Agent

Always be polite and professional."""

# Avoid
instructions = "Help users"
```
