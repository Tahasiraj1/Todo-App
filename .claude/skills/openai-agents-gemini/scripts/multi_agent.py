#!/usr/bin/env python3
"""
Multi-Agent System with Handoffs

This example demonstrates creating a multi-agent system with handoffs
using the OpenAI Agents SDK with Google Gemini.

Requirements:
    pip install openai-agents openai

Environment:
    export GEMINI_API_KEY="your-gemini-api-key"

Usage:
    python multi_agent.py
"""

import asyncio
import os

from agents import Agent, Runner, function_tool, handoff, set_tracing_disabled
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


# ============================================================
# Tools for specialized agents
# ============================================================

@function_tool
def check_order_status(order_id: str) -> str:
    """Check the status of an order.

    Args:
        order_id: The order ID to check (e.g., "ORD-12345")
    """
    # Simulated order database
    orders = {
        "ORD-12345": {"status": "Shipped", "eta": "2024-01-20"},
        "ORD-67890": {"status": "Processing", "eta": "2024-01-25"},
        "ORD-11111": {"status": "Delivered", "delivered": "2024-01-15"},
    }

    if order_id in orders:
        order = orders[order_id]
        if order["status"] == "Delivered":
            return f"Order {order_id}: Delivered on {order['delivered']}"
        else:
            return f"Order {order_id}: {order['status']}, ETA: {order['eta']}"
    else:
        return f"Order {order_id} not found. Please verify the order ID."


@function_tool
def process_refund(order_id: str, reason: str) -> str:
    """Process a refund request for an order.

    Args:
        order_id: The order ID to refund
        reason: The reason for the refund
    """
    return f"Refund initiated for order {order_id}. Reason: {reason}. " \
           f"Refund will be processed within 5-7 business days."


@function_tool
def update_shipping_address(order_id: str, new_address: str) -> str:
    """Update the shipping address for an order.

    Args:
        order_id: The order ID to update
        new_address: The new shipping address
    """
    return f"Shipping address for order {order_id} updated to: {new_address}"


@function_tool
def get_product_info(product_name: str) -> str:
    """Get information about a product.

    Args:
        product_name: The name of the product to look up
    """
    products = {
        "laptop": {"price": "$999", "stock": "In stock", "delivery": "2-3 days"},
        "headphones": {"price": "$199", "stock": "In stock", "delivery": "1-2 days"},
        "keyboard": {"price": "$149", "stock": "Low stock", "delivery": "3-5 days"},
    }

    for name, info in products.items():
        if name in product_name.lower():
            return f"{name.title()}: {info['price']}, {info['stock']}, Ships in {info['delivery']}"

    return f"Product '{product_name}' not found. Try: laptop, headphones, keyboard"


@function_tool
def apply_discount_code(code: str) -> str:
    """Apply a discount code.

    Args:
        code: The discount code to apply
    """
    codes = {
        "SAVE10": "10% discount applied!",
        "FREESHIP": "Free shipping applied!",
        "WELCOME": "15% new customer discount applied!",
    }

    return codes.get(code.upper(), f"Invalid discount code: {code}")


# ============================================================
# Specialized Agents
# ============================================================

def create_agents():
    """Create the multi-agent system."""

    gemini_model = get_gemini_model()

    # Order Support Agent
    order_agent = Agent(
        name="Order Support Agent",
        instructions="""You are an order support specialist.
You help customers with:
- Checking order status
- Updating shipping addresses
- General order inquiries

Use your tools to look up order information.
Be helpful and provide accurate information.
If you cannot resolve the issue, let the customer know.""",
        model=gemini_model,
        tools=[check_order_status, update_shipping_address],
    )

    # Refund Agent
    refund_agent = Agent(
        name="Refund Agent",
        instructions="""You are a refund specialist.
You help customers with refund requests.

Before processing a refund:
1. Confirm the order ID
2. Ask for the reason for the refund
3. Process the refund using your tool

Be empathetic and efficient.""",
        model=gemini_model,
        tools=[process_refund],
    )

    # Sales Agent
    sales_agent = Agent(
        name="Sales Agent",
        instructions="""You are a sales specialist.
You help customers with:
- Product information and recommendations
- Pricing questions
- Discount codes

Use your tools to provide accurate product information.
Be enthusiastic but not pushy.""",
        model=gemini_model,
        tools=[get_product_info, apply_discount_code],
    )

    # Triage Agent (main entry point)
    triage_agent = Agent(
        name="Customer Service Triage",
        instructions="""You are the first point of contact for customer service.
Your job is to understand the customer's needs and route them appropriately.

ROUTING RULES:
- ORDER STATUS or SHIPPING QUESTIONS → Hand off to Order Support Agent
- REFUND or RETURN REQUESTS → Hand off to Refund Agent
- PRODUCT INFO, PRICING, or DISCOUNT CODES → Hand off to Sales Agent

For simple greetings or general questions, you can answer directly.
Be friendly and efficient in routing customers to the right specialist.""",
        model=gemini_model,
        handoffs=[
            handoff(
                order_agent,
                tool_name="transfer_to_orders",
                tool_description="Transfer to Order Support for order status, tracking, and shipping questions"
            ),
            handoff(
                refund_agent,
                tool_name="transfer_to_refunds",
                tool_description="Transfer to Refund Agent for return and refund requests"
            ),
            handoff(
                sales_agent,
                tool_name="transfer_to_sales",
                tool_description="Transfer to Sales Agent for product info, pricing, and discounts"
            ),
        ],
    )

    return triage_agent


async def main():
    """Run the multi-agent example."""
    print("Creating multi-agent customer service system...")

    triage_agent = create_agents()

    print("System ready!\n")

    print("=" * 60)
    print("Customer Service Chat")
    print("=" * 60)
    print("Try these scenarios:")
    print("  - 'What's the status of order ORD-12345?'")
    print("  - 'I want a refund for order ORD-67890'")
    print("  - 'How much does the laptop cost?'")
    print("  - 'I have a discount code SAVE10'")
    print("Type 'quit' to exit")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nCustomer: ").strip()

            if user_input.lower() in ('quit', 'exit', 'q'):
                print("Thank you for contacting us. Goodbye!")
                break

            if not user_input:
                continue

            # Run the agent
            result = await Runner.run(triage_agent, input=user_input)

            # Show which agent handled the request
            if result.last_agent.name != triage_agent.name:
                print(f"\n[Transferred to: {result.last_agent.name}]")

            print(f"\nAgent: {result.final_output}")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
