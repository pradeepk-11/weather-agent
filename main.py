"""
Weather Agent Web App
FastAPI wrapper around the ADK agent — serves as the Cloud Run endpoint.
"""

import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from agent.agent import run_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Weather Agent API starting up...")
    yield
    print("Weather Agent API shutting down...")


app = FastAPI(
    title="Weather Intelligence Agent",
    description="ADK agent powered by MCP + OpenWeatherMap",
    version="1.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    status: str = "ok"


@app.get("/", response_class=HTMLResponse)
async def root():
    """Simple UI for testing the agent."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Weather Agent</title>
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: system-ui, sans-serif; background: #f5f5f5; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 2rem 1rem; }
        h1 { font-size: 1.5rem; font-weight: 600; color: #1a1a1a; margin-bottom: .25rem; }
        p.sub { font-size: .875rem; color: #666; margin-bottom: 1.5rem; }
        .chat-box { background: white; border-radius: 12px; border: 1px solid #e5e5e5; width: 100%; max-width: 640px; padding: 1.5rem; min-height: 300px; margin-bottom: 1rem; font-size: .9rem; line-height: 1.6; color: #333; white-space: pre-wrap; }
        .input-row { display: flex; gap: 8px; width: 100%; max-width: 640px; }
        input { flex: 1; padding: .65rem 1rem; border: 1px solid #ddd; border-radius: 8px; font-size: .9rem; outline: none; }
        input:focus { border-color: #1D9E75; }
        button { padding: .65rem 1.25rem; background: #1D9E75; color: white; border: none; border-radius: 8px; font-size: .9rem; cursor: pointer; font-weight: 500; }
        button:hover { background: #0F6E56; }
        button:disabled { background: #aaa; cursor: not-allowed; }
        .examples { margin-top: 1rem; display: flex; gap: 8px; flex-wrap: wrap; width: 100%; max-width: 640px; }
        .ex { font-size: .8rem; padding: 4px 12px; border: 1px solid #ddd; border-radius: 20px; cursor: pointer; color: #444; background: white; }
        .ex:hover { border-color: #1D9E75; color: #1D9E75; }
      </style>
    </head>
    <body>
      <h1>🌤 Weather Intelligence Agent</h1>
      <p class="sub">Powered by Google ADK + MCP + OpenWeatherMap</p>
      <div class="chat-box" id="output">Ask me about the weather anywhere in the world...</div>
      <div class="input-row">
        <input id="msg" type="text" placeholder="e.g. What's the weather in Tokyo?" onkeydown="if(event.key==='Enter') send()">
        <button id="btn" onclick="send()">Ask</button>
      </div>
      <div class="examples">
        <span class="ex" onclick="ask('What is the weather in Mumbai right now?')">Mumbai now</span>
        <span class="ex" onclick="ask('Give me a 3-day forecast for London')">London 3-day</span>
        <span class="ex" onclick="ask('Is it a good day to go outside in New York?')">NYC outdoors?</span>
        <span class="ex" onclick="ask('Compare weather in Paris and Berlin')">Paris vs Berlin</span>
      </div>
      <script>
        function ask(q) { document.getElementById('msg').value = q; send(); }
        async function send() {
          const msg = document.getElementById('msg').value.trim();
          if (!msg) return;
          const out = document.getElementById('output');
          const btn = document.getElementById('btn');
          out.textContent = 'Fetching weather data...';
          btn.disabled = true;
          document.getElementById('msg').value = '';
          try {
            const r = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: msg }) });
            const d = await r.json();
            out.textContent = d.response || d.detail || 'Something went wrong.';
          } catch(e) { out.textContent = 'Error: ' + e.message; }
          btn.disabled = false;
        }
      </script>
    </body>
    </html>
    """


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main endpoint — takes a user message, returns agent response."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        response = await run_agent(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@app.get("/health")
async def health():
    """Health check for Cloud Run."""
    return {"status": "healthy", "service": "weather-agent"}
