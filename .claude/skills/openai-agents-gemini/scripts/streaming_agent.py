#!/usr/bin/env python3
"""
Streaming Agent with Google Gemini

This example demonstrates streaming responses from an agent using
the OpenAI Agents SDK with Google Gemini.

Requirements:
    pip install openai-agents openai

Environment:
    export GEMINI_API_KEY="your-gemini-api-key"

Usage:
    python streaming_agent.py
"""

import asyncio
import os
import sys

from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI


def get_gemini_model(model_name: str = "gemini-2.5-flash-preview-05-20") -> OpenAIChatCompletionsModel:
    """Create a Gemini model instance."""
    set_tracing_disabled(disabled=True)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    provider = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=api_key,
    )

    return OpenAIChatCompletionsModel(
        openai_client=provider,
        model=model_name
    )


@function_tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for information.

    Args:
        query: The search query
    """
    # Simulated knowledge base
    knowledge = {
        "python": "Python is a high-level, interpreted programming language known for its readability and versatility.",
        "javascript": "JavaScript is a lightweight, interpreted programming language primarily used for web development.",
        "rust": "Rust is a systems programming language focused on safety, speed, and concurrency.",
        "ai": "Artificial Intelligence (AI) refers to the simulation of human intelligence in machines.",
        "machine learning": "Machine Learning is a subset of AI that enables systems to learn from data.",
    }

    for key, info in knowledge.items():
        if key in query.lower():
            return f"Found: {info}"

    return f"No specific information found for '{query}'. The agent will use general knowledge."


async def stream_response(agent: Agent, user_input: str):
    """Stream the agent's response with real-time output."""
    print("\nAssistant: ", end="", flush=True)

    try:
        # Start streaming run
        result = Runner.run_streamed(agent, input=user_input)

        # Track what we've seen
        text_started = False
        tool_calls = []

        # Process stream events
        async for event in result.stream_events():
            event_type = type(event).__name__

            # Handle text delta events (streaming text)
            if hasattr(event, 'delta') and event.delta:
                text_started = True
                print(event.delta, end="", flush=True)

            # Handle tool call events
            elif 'ToolCall' in event_type:
                if hasattr(event, 'name'):
                    tool_calls.append(event.name)
                    if not text_started:
                        print(f"[Using tool: {event.name}]", end=" ", flush=True)

            # Handle tool result events
            elif 'ToolResult' in event_type:
                pass  # Tool result will be incorporated into response

        # Ensure we end with a newline
        print()

        # Get final output (in case streaming missed something)
        final_output = await result.final_output

        return final_output

    except Exception as e:
        print(f"\nError during streaming: {e}")
        return None


async def main():
    """Run the streaming agent example."""
    print("Creating streaming Gemini-powered agent...")

    gemini_model = get_gemini_model()

    agent = Agent(
        name="Streaming Assistant",
        instructions="""You are a helpful assistant that provides detailed, informative responses.
You have access to a knowledge base that you can search for specific topics.

When answering questions:
- Provide comprehensive but well-organized responses
- Use the search tool when you need specific technical information
- Break down complex topics into understandable parts
- Use examples when helpful

Your responses will be streamed in real-time, so maintain a natural flow.""",
        model=gemini_model,
        tools=[search_knowledge_base],
    )

    print("Agent ready for streaming responses!\n")

    print("=" * 60)
    print("Streaming Chat Demo")
    print("=" * 60)
    print("Try asking for detailed explanations:")
    print("  - 'Explain how Python works'")
    print("  - 'What is machine learning?'")
    print("  - 'Write a short story about a robot'")
    print("Type 'quit' to exit")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ('quit', 'exit', 'q'):
                print("Goodbye!")
                break

            if not user_input:
                continue

            # Stream the response
            await stream_response(agent, user_input)

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


async def demo_streaming():
    """Quick demo of streaming capabilities."""
    print("=" * 60)
    print("Streaming Demo - Watch the response appear in real-time")
    print("=" * 60)

    gemini_model = get_gemini_model()

    agent = Agent(
        name="Demo Agent",
        instructions="You provide detailed, educational responses. Explain concepts clearly.",
        model=gemini_model,
    )

    demo_prompts = [
        "Explain what makes a good programming language in 3-4 sentences.",
        "What are the key benefits of cloud computing?",
    ]

    for prompt in demo_prompts:
        print(f"\nPrompt: {prompt}")
        await stream_response(agent, prompt)
        print("-" * 40)


if __name__ == "__main__":
    # Check for demo mode
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(demo_streaming())
    else:
        asyncio.run(main())
