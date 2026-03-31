"""
Weather MCP Server
Exposes weather data tools to any MCP client (including ADK agents).
"""

import os
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org/data/2.5"


@mcp.tool()
async def get_current_weather(city: str, units: str = "metric") -> dict:
    """
    Get current weather for a city.

    Args:
        city: City name (e.g. 'Mumbai', 'London', 'New York')
        units: 'metric' (Celsius), 'imperial' (Fahrenheit), or 'standard' (Kelvin)

    Returns:
        dict with temperature, feels_like, humidity, wind_speed, description, and city info
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY environment variable not set."}

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/weather",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": units,
            },
            timeout=10,
        )

    if resp.status_code == 404:
        return {"error": f"City '{city}' not found. Please check the spelling."}
    if resp.status_code == 401:
        return {"error": "Invalid API key. Check your OPENWEATHER_API_KEY."}
    resp.raise_for_status()

    data = resp.json()
    unit_symbol = "°C" if units == "metric" else "°F" if units == "imperial" else "K"

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": f"{data['main']['temp']}{unit_symbol}",
        "feels_like": f"{data['main']['feels_like']}{unit_symbol}",
        "humidity": f"{data['main']['humidity']}%",
        "wind_speed": f"{data['wind']['speed']} {'m/s' if units == 'metric' else 'mph'}",
        "description": data["weather"][0]["description"].capitalize(),
        "visibility": f"{data.get('visibility', 'N/A')} m",
    }


@mcp.tool()
async def get_weather_forecast(city: str, days: int = 3, units: str = "metric") -> dict:
    """
    Get a multi-day weather forecast for a city (up to 5 days).

    Args:
        city: City name
        days: Number of days (1-5)
        units: 'metric', 'imperial', or 'standard'

    Returns:
        dict with daily forecast summaries
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "OPENWEATHER_API_KEY environment variable not set."}

    days = max(1, min(days, 5))

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/forecast",
            params={
                "q": city,
                "appid": OPENWEATHER_API_KEY,
                "units": units,
                "cnt": days * 8,  # API returns 3-hour intervals; 8 per day
            },
            timeout=10,
        )

    if resp.status_code == 404:
        return {"error": f"City '{city}' not found."}
    resp.raise_for_status()

    data = resp.json()
    unit_symbol = "°C" if units == "metric" else "°F" if units == "imperial" else "K"

    # Aggregate by day (take midday reading ~12:00)
    daily = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]
        hour = item["dt_txt"].split(" ")[1]
        if date not in daily or hour == "12:00:00":
            daily[date] = {
                "date": date,
                "temp": f"{item['main']['temp']}{unit_symbol}",
                "temp_min": f"{item['main']['temp_min']}{unit_symbol}",
                "temp_max": f"{item['main']['temp_max']}{unit_symbol}",
                "description": item["weather"][0]["description"].capitalize(),
                "humidity": f"{item['main']['humidity']}%",
                "wind_speed": f"{item['wind']['speed']} {'m/s' if units == 'metric' else 'mph'}",
            }

    return {
        "city": data["city"]["name"],
        "country": data["city"]["country"],
        "forecast": list(daily.values())[:days],
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
