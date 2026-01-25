---
name: openai-agents-gemini
description: |
  Builds AI agents using OpenAI Agents SDK with Google Gemini models instead of OpenAI models.
  This skill should be used when users want to create multi-agent systems, tools, handoffs, or
  agentic workflows using the OpenAI Agents SDK architecture but powered by Google Gemini.
  Always use GEMINI_API_KEY and Gemini endpoints, never OpenAI credentials.
---

# OpenAI Agents SDK with Google Gemini Integration

## Overview

This skill enables building production-grade AI agents using the **OpenAI Agents SDK** architecture but with **Google Gemini models** as the LLM backend. The SDK's patterns (agents, tools, handoffs, runners) remain identical—only the model initialization differs.

## What This Skill Does

- Creates agents using OpenAI Agents SDK with Gemini models
- Implements the Gemini model wrapper pattern correctly
- Builds tools using `@function_tool` decorator
- Sets up agent handoffs for multi-agent systems
- Configures `Runner.run()` and `Runner.run_streamed()` execution
- Applies `ModelSettings` for tool choice configuration
- Handles async/sync agent execution patterns

## What It Does NOT Do

- Use OpenAI API keys or OpenAI model names
- Configure OpenAI-specific tracing (disabled for Gemini)
- Use the OpenAI Responses API (uses Chat Completions instead)
- Handle OpenAI-specific features not supported by Gemini

## Critical: Gemini Model Integration

**ALWAYS use this pattern for Gemini integration:**

```python
import os
from agents import Agent, Runner, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

def get_gemini_model(model_name: str = "gemini-2.5-flash-preview-05-20"):
    """Create a Gemini model instance for use with OpenAI Agents SDK."""
    # Disable tracing (not supported with Gemini)
    set_tracing_disabled(disabled=True)

    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    # Create provider pointing to Gemini's OpenAI-compatible endpoint
    provider = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key,
    )

    # Wrap with OpenAIChatCompletionsModel
    model = OpenAIChatCompletionsModel(
        openai_client=provider,
        model=model_name
    )

    return model
```

**Key requirements:**
- Environment variable: `GEMINI_API_KEY` (NOT `OPENAI_API_KEY`)
- Base URL: `https://generativelanguage.googleapis.com/v1beta/openai/`
- Use `OpenAIChatCompletionsModel` wrapper
- Disable tracing with `set_tracing_disabled(disabled=True)`

## Available Gemini Models

| Model | Use Case |
|-------|----------|
| `gemini-2.5-flash-preview-05-20` | Fast, cost-effective (recommended) |
| `gemini-2.5-pro-preview-05-06` | High capability tasks |
| `gemini-2.0-flash` | Stable production model |
| `gemini-1.5-pro` | Legacy high-capability |
| `gemini-1.5-flash` | Legacy fast model |

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing agent patterns, tool definitions |
| **Conversation** | User's specific agent requirements |
| **Skill References** | SDK patterns from `references/` |
| **Environment** | Verify `GEMINI_API_KEY` is set |

## Required Clarifications

### Agent Type
- Single agent or multi-agent system?
- Need handoffs between agents?

### Tools Required
- What tools should the agent have?
- Sync or async tool functions?

### Execution Mode
- Synchronous (`Runner.run`) or streaming (`Runner.run_streamed`)?
- Need to process stream events?

## Core Patterns

### Pattern 1: Basic Agent with Gemini

```python
import asyncio
import os
from agents import Agent, Runner, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

# Setup Gemini model
set_tracing_disabled(disabled=True)

gemini_model = OpenAIChatCompletionsModel(
    openai_client=AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    model="gemini-2.5-flash-preview-05-20"
)

# Create agent
agent = Agent(
    name="Assistant",
    instructions="You are a helpful assistant.",
    model=gemini_model,
)

# Run agent
async def main():
    result = await Runner.run(agent, input="Hello!")
    print(result.final_output)

asyncio.run(main())
```

### Pattern 2: Agent with Tools

```python
from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
import os

set_tracing_disabled(disabled=True)

# Define tools using @function_tool decorator
@function_tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The name of the city to get weather for.
    """
    # Implement actual weather API call
    return f"The weather in {city} is sunny, 72°F"

@function_tool
async def search_database(query: str) -> str:
    """Search the database for information.

    Args:
        query: The search query string.
    """
    # Implement actual database search
    return f"Found 5 results for: {query}"

# Create Gemini model
gemini_model = OpenAIChatCompletionsModel(
    openai_client=AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    model="gemini-2.5-flash-preview-05-20"
)

# Create agent with tools
agent = Agent(
    name="Research Assistant",
    instructions="Help users find information. Use tools when needed.",
    model=gemini_model,
    tools=[get_weather, search_database],
)
```

### Pattern 3: Multi-Agent Handoffs

```python
from agents import Agent, Runner, handoff, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
import os

set_tracing_disabled(disabled=True)

# Shared Gemini model
def create_gemini_model():
    return OpenAIChatCompletionsModel(
        openai_client=AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("GEMINI_API_KEY"),
        ),
        model="gemini-2.5-flash-preview-05-20"
    )

# Specialized agents
booking_agent = Agent(
    name="Booking Agent",
    instructions="You help users book appointments and reservations.",
    model=create_gemini_model(),
)

support_agent = Agent(
    name="Support Agent",
    instructions="You handle customer support and technical issues.",
    model=create_gemini_model(),
)

# Triage agent with handoffs
triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are the first point of contact.
    - For booking requests, hand off to Booking Agent
    - For support issues, hand off to Support Agent
    """,
    model=create_gemini_model(),
    handoffs=[booking_agent, support_agent],
)

# Run with handoffs
async def main():
    result = await Runner.run(
        triage_agent,
        input="I need to book a meeting room for tomorrow"
    )
    print(f"Final agent: {result.last_agent.name}")
    print(f"Output: {result.final_output}")
```

### Pattern 4: Streaming Responses

```python
from agents import Agent, Runner, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
import os

set_tracing_disabled(disabled=True)

gemini_model = OpenAIChatCompletionsModel(
    openai_client=AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    model="gemini-2.5-flash-preview-05-20"
)

agent = Agent(
    name="Streaming Assistant",
    instructions="Provide detailed responses.",
    model=gemini_model,
)

async def main():
    # Use run_streamed for streaming
    result = Runner.run_streamed(agent, input="Explain quantum computing")

    async for event in result.stream_events():
        # Process stream events
        if hasattr(event, 'delta'):
            print(event.delta, end='', flush=True)

    # Get final result
    final = await result.final_output
    print(f"\n\nFinal: {final}")
```

### Pattern 5: Model Settings Configuration

```python
from agents import Agent, Runner, ModelSettings, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
import os

set_tracing_disabled(disabled=True)

gemini_model = OpenAIChatCompletionsModel(
    openai_client=AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    model="gemini-2.5-flash-preview-05-20"
)

# Configure model settings
agent = Agent(
    name="Configured Agent",
    instructions="You are helpful.",
    model=gemini_model,
    model_settings=ModelSettings(
        temperature=0.7,
        max_tokens=2000,
        tool_choice="auto",  # or "required", "none"
    ),
)
```

### Pattern 6: RunConfig for Advanced Control

```python
from agents import Agent, Runner, RunConfig, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
import os

set_tracing_disabled(disabled=True)

gemini_model = OpenAIChatCompletionsModel(
    openai_client=AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY"),
    ),
    model="gemini-2.5-flash-preview-05-20"
)

agent = Agent(
    name="Advanced Agent",
    instructions="You are helpful.",
    model=gemini_model,
)

async def main():
    result = await Runner.run(
        agent,
        input="Help me with a task",
        run_config=RunConfig(
            max_turns=10,
            tracing_disabled=True,
            workflow_name="My Workflow",
        ),
    )
    print(result.final_output)
```

## Environment Setup

```bash
# Required: Set Gemini API key
export GEMINI_API_KEY="your-gemini-api-key"

# Install dependencies
pip install openai-agents openai
```

## Common Issues and Solutions

### Issue: 404 Error on API Call

**Cause**: Using Responses API instead of Chat Completions
**Solution**: Use `OpenAIChatCompletionsModel` wrapper (shown in patterns above)

### Issue: Authentication Error

**Cause**: Missing or invalid `GEMINI_API_KEY`
**Solution**: Ensure environment variable is set correctly

### Issue: Tracing Errors

**Cause**: OpenAI tracing not compatible with Gemini
**Solution**: Always call `set_tracing_disabled(disabled=True)`

### Issue: Model Not Found

**Cause**: Invalid Gemini model name
**Solution**: Use exact model names from the Available Gemini Models table

## Output Checklist

- [ ] Uses `GEMINI_API_KEY` environment variable
- [ ] Base URL is `https://generativelanguage.googleapis.com/v1beta/openai/`
- [ ] Uses `OpenAIChatCompletionsModel` wrapper
- [ ] Tracing is disabled with `set_tracing_disabled(disabled=True)`
- [ ] Model name is a valid Gemini model
- [ ] Tools use `@function_tool` decorator
- [ ] Async functions use `await` correctly
- [ ] Handoffs are configured correctly for multi-agent

## Reference Files

| File | Purpose |
|------|---------|
| `references/sdk-patterns.md` | OpenAI Agents SDK core patterns |
| `references/tool-patterns.md` | Tool creation and usage patterns |
| `references/handoff-patterns.md` | Multi-agent handoff patterns |
| `references/troubleshooting.md` | Common issues and solutions |
| `scripts/basic_agent.py` | Basic agent example |
| `scripts/multi_agent.py` | Multi-agent handoff example |
| `scripts/streaming_agent.py` | Streaming response example |

---

**Remember**: This skill uses OpenAI Agents SDK patterns but ALWAYS with Google Gemini models. Never use OpenAI API keys or OpenAI model names.
