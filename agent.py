"""
Weather ADK Agent
Uses Google ADK to connect to the Weather MCP server via MCP protocol.
"""

import os
import asyncio
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams


MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://localhost:8000/mcp")

SYSTEM_PROMPT = """You are a friendly and helpful weather assistant. 

When a user asks about the weather:
1. Use the get_current_weather tool for current conditions
2. Use the get_weather_forecast tool when they ask about upcoming days
3. Always provide practical advice based on the weather (what to wear, whether to carry an umbrella, etc.)
4. Be conversational and warm in your responses
5. If the user doesn't specify a city, ask them which city they want weather for

Keep responses concise but informative. Always include the key details: temperature, conditions, and any relevant advice.
"""


def create_weather_agent() -> LlmAgent:
    """Create and return the weather ADK agent connected to MCP server."""
    toolset = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MCP_SERVER_URL,
        )
    )

    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="weather_agent",
        description="A weather assistant that fetches real-time weather data.",
        instruction=SYSTEM_PROMPT,
        tools=[toolset],
    )

    return agent


async def run_agent(user_message: str) -> str:
    """Run the agent with a user message and return the response."""
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai import types

    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="weather_agent",
        user_id="user_001",
    )

    runner = Runner(
        agent=create_weather_agent(),
        app_name="weather_agent",
        session_service=session_service,
    )

    content = types.Content(
        role="user",
        parts=[types.Part(text=user_message)],
    )

    response_text = ""
    async for event in runner.run_async(
        user_id="user_001",
        session_id=session.id,
        new_message=content,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    response_text += part.text

    return response_text


if __name__ == "__main__":
    async def main():
        print("Weather Agent ready. Type 'quit' to exit.\n")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ("quit", "exit"):
                break
            if not user_input:
                continue
            print("Agent: thinking...")
            response = await run_agent(user_input)
            print(f"Agent: {response}\n")

    asyncio.run(main())
