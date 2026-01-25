# Multi-Agent Handoff Patterns

This reference covers creating multi-agent systems with handoffs using the OpenAI Agents SDK.

## Basic Handoff

The simplest way to enable handoffs is to pass agents directly to the `handoffs` parameter.

```python
from agents import Agent

# Specialized agents
sales_agent = Agent(
    name="Sales Agent",
    instructions="You handle sales inquiries and product information.",
    model=gemini_model,
)

support_agent = Agent(
    name="Support Agent",
    instructions="You handle technical support and troubleshooting.",
    model=gemini_model,
)

# Main agent with handoffs
triage_agent = Agent(
    name="Triage Agent",
    instructions="""You are the first point of contact.
    - For sales questions, hand off to Sales Agent
    - For support issues, hand off to Support Agent
    Be brief and hand off quickly when appropriate.""",
    model=gemini_model,
    handoffs=[sales_agent, support_agent],
)
```

## Using handoff() Function

For more control, use the `handoff()` function.

```python
from agents import Agent, handoff

billing_agent = Agent(
    name="Billing Agent",
    instructions="Handle billing and payment issues.",
    model=gemini_model,
)

# Basic handoff
simple_handoff = handoff(billing_agent)

# Handoff with custom tool description
descriptive_handoff = handoff(
    billing_agent,
    tool_description="Transfer to billing specialist for payment issues"
)

# Handoff with custom tool name
named_handoff = handoff(
    billing_agent,
    tool_name="transfer_to_billing",
    tool_description="Transfer conversation to billing department"
)

main_agent = Agent(
    name="Main Agent",
    instructions="Route users to appropriate departments.",
    model=gemini_model,
    handoffs=[descriptive_handoff],
)
```

## Handoff with Input Filter

Control what context is passed to the next agent.

```python
from agents import Agent, handoff, HandoffInputData

def filter_sensitive_data(input_data: HandoffInputData) -> HandoffInputData:
    """Remove sensitive information before handoff."""
    # Filter conversation history
    filtered_history = []
    for item in input_data.history:
        # Remove items containing sensitive keywords
        if hasattr(item, 'content'):
            if 'password' not in str(item.content).lower():
                filtered_history.append(item)

    return HandoffInputData(
        history=filtered_history,
        pre_handoff_items=input_data.pre_handoff_items,
    )

secure_agent = Agent(
    name="Secure Agent",
    instructions="Handle secure operations.",
    model=gemini_model,
)

main_agent = Agent(
    name="Main Agent",
    instructions="...",
    model=gemini_model,
    handoffs=[
        handoff(secure_agent, input_filter=filter_sensitive_data)
    ],
)
```

## Circular Handoffs

Agents can hand back to previous agents.

```python
from agents import Agent

# Forward declaration pattern for circular references
escalation_agent = Agent(
    name="Escalation Agent",
    instructions="""Handle escalated issues.
    If issue is resolved, hand back to Support Agent.""",
    model=gemini_model,
    handoffs=[],  # Will be set later
)

support_agent = Agent(
    name="Support Agent",
    instructions="""Handle support requests.
    If unable to resolve, escalate to Escalation Agent.""",
    model=gemini_model,
    handoffs=[escalation_agent],
)

# Complete the circular reference
escalation_agent.handoffs = [support_agent]
```

## Hierarchical Multi-Agent System

```python
from agents import Agent

# Level 3: Specialist agents
billing_specialist = Agent(
    name="Billing Specialist",
    instructions="Expert in complex billing issues.",
    model=gemini_model,
)

tech_specialist = Agent(
    name="Technical Specialist",
    instructions="Expert in complex technical issues.",
    model=gemini_model,
)

# Level 2: Department agents
billing_agent = Agent(
    name="Billing Department",
    instructions="""Handle billing inquiries.
    Escalate complex issues to Billing Specialist.""",
    model=gemini_model,
    handoffs=[billing_specialist],
)

tech_agent = Agent(
    name="Technical Support",
    instructions="""Handle technical issues.
    Escalate complex issues to Technical Specialist.""",
    model=gemini_model,
    handoffs=[tech_specialist],
)

# Level 1: Triage
triage_agent = Agent(
    name="Customer Service",
    instructions="""Greet customers and route appropriately.
    - Billing questions → Billing Department
    - Technical issues → Technical Support""",
    model=gemini_model,
    handoffs=[billing_agent, tech_agent],
)
```

## Handoff with Conditional Logic

```python
from agents import Agent, handoff, RunContextWrapper

def should_escalate(ctx: RunContextWrapper) -> bool:
    """Check if conversation should be escalated."""
    return ctx.context.get("escalate", False)

# Create conditional handoff using is_enabled
@function_tool(is_enabled=should_escalate)
def escalate_to_manager() -> str:
    """Escalate to manager."""
    return "Escalating..."

manager_agent = Agent(
    name="Manager",
    instructions="Handle escalated issues.",
    model=gemini_model,
)

support_agent = Agent(
    name="Support",
    instructions="""Handle support requests.
    Set context['escalate']=True to enable escalation.""",
    model=gemini_model,
    handoffs=[manager_agent],
)
```

## Tracking Handoffs

```python
from agents import Agent, Runner

async def main():
    result = await Runner.run(
        triage_agent,
        input="I need help with my bill",
    )

    # Check which agent handled the final response
    print(f"Final agent: {result.last_agent.name}")

    # Track handoff chain
    agents_involved = []
    for item in result.new_items:
        if hasattr(item, 'agent'):
            if item.agent.name not in agents_involved:
                agents_involved.append(item.agent.name)

    print(f"Agents involved: {' → '.join(agents_involved)}")
```

## Handoff Best Practices

### 1. Clear Handoff Instructions

```python
# Good - specific handoff criteria
triage_agent = Agent(
    name="Triage",
    instructions="""Route customers based on their needs:

    HAND OFF TO SALES AGENT when:
    - Customer asks about pricing
    - Customer wants to make a purchase
    - Customer asks about product features

    HAND OFF TO SUPPORT AGENT when:
    - Customer reports a bug or error
    - Customer needs help using a feature
    - Customer has a technical question

    Stay and help when:
    - Customer has a general question
    - Customer wants to know business hours
    """,
    model=gemini_model,
    handoffs=[sales_agent, support_agent],
)

# Avoid - vague instructions
bad_agent = Agent(
    name="Triage",
    instructions="Help users and hand off when needed.",
    handoffs=[sales_agent, support_agent],
)
```

### 2. Descriptive Tool Names

```python
# Good - clear tool descriptions
handoffs=[
    handoff(
        billing_agent,
        tool_name="transfer_to_billing",
        tool_description="Transfer to billing for payment, invoices, or subscription issues"
    ),
    handoff(
        tech_agent,
        tool_name="transfer_to_tech_support",
        tool_description="Transfer to tech support for bugs, errors, or technical help"
    ),
]

# Avoid - unclear descriptions
handoffs=[billing_agent, tech_agent]  # No context for the model
```

### 3. Limit Handoff Depth

```python
# Good - limited handoff chain
# Triage → Department → Specialist (max 3 levels)

# Avoid - too many handoff levels
# Can lead to confusion and lost context
```

### 4. Test Handoff Scenarios

```python
async def test_handoffs():
    # Test billing handoff
    result = await Runner.run(triage_agent, "I have a billing question")
    assert result.last_agent.name == "Billing Agent"

    # Test support handoff
    result = await Runner.run(triage_agent, "My app is crashing")
    assert result.last_agent.name == "Support Agent"

    # Test no handoff
    result = await Runner.run(triage_agent, "What are your hours?")
    assert result.last_agent.name == "Triage"
```

## RunConfig for Handoffs

```python
from agents import Runner, RunConfig

result = await Runner.run(
    triage_agent,
    input="Complex issue...",
    run_config=RunConfig(
        # Global handoff settings
        nest_handoff_history=True,  # Wrap history for new agent

        # Limit total turns across all agents
        max_turns=20,
    ),
)
```
