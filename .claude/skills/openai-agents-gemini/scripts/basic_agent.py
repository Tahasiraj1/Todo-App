#!/usr/bin/env python3
"""
Basic Agent with Google Gemini

This example demonstrates creating a simple agent using the OpenAI Agents SDK
with Google Gemini as the LLM backend.

Requirements:
    pip install openai-agents openai

Environment:
    export GEMINI_API_KEY="your-gemini-api-key"

Usage:
    python basic_agent.py
"""

import asyncio
import os
from typing import Optional

from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI


def get_gemini_model(model_name: str = "gemini-2.5-flash-preview-05-20") -> OpenAIChatCompletionsModel:
    """
    Create a Gemini model instance for use with OpenAI Agents SDK.

    Args:
        model_name: The Gemini model to use. Options include:
            - gemini-2.5-flash-preview-05-20 (fast, recommended)
            - gemini-2.5-pro-preview-05-06 (high capability)
            - gemini-2.0-flash (stable)

    Returns:
        OpenAIChatCompletionsModel configured for Gemini

    Raises:
        ValueError: If GEMINI_API_KEY is not set
    """
    # Disable tracing (not supported with Gemini)
    set_tracing_disabled(disabled=True)

    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get your key from https://aistudio.google.com/apikey"
        )

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


# Define a simple tool
@function_tool
def get_current_time() -> str:
    """Get the current date and time.

    Returns the current date and time in a human-readable format.
    """
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@function_tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")

    Returns:
        The result of the calculation or an error message.
    """
    try:
        # Only allow safe mathematical operations
        allowed_chars = set("0123456789+-*/(). ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Only basic math operations are allowed"

        result = eval(expression)  # Safe due to character whitelist
        return f"{expression} = {result}"
    except Exception as e:
        return f"Error: Could not evaluate '{expression}': {str(e)}"


async def main():
    """Run the basic agent example."""
    print("Creating Gemini-powered agent...")

    # Create the Gemini model
    gemini_model = get_gemini_model()

    # Create the agent
    agent = Agent(
        name="Assistant",
        instructions="""You are a helpful assistant powered by Google Gemini.

You can:
- Answer questions about various topics
- Use the get_current_time tool to tell the current time
- Use the calculate tool for math calculations

Be friendly, concise, and helpful.""",
        model=gemini_model,
        tools=[get_current_time, calculate],
    )

    print("Agent created successfully!\n")

    # Interactive conversation loop
    print("=" * 50)
    print("Chat with the Gemini-powered agent")
    print("Type 'quit' to exit")
    print("=" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break

            if not user_input:
                continue

            # Run the agent
            result = await Runner.run(agent, input=user_input)

            print(f"\nAssistant: {result.final_output}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
