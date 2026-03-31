# 🌤 Weather Intelligence Agent
### ADK Agent + MCP Server + OpenWeatherMap | Google Cloud Run

A production-ready AI agent built with **Google ADK** that uses **Model Context Protocol (MCP)** to connect to OpenWeatherMap and deliver real-time weather insights.

---

## Architecture

```
User → Agent Web App (Cloud Run)
           ↓  ADK + Gemini 2.0
       MCP Client
           ↓  MCP Protocol (HTTP)
       MCP Server (Cloud Run)
           ↓  REST API
       OpenWeatherMap API
```

- **MCP Server** — exposes `get_current_weather` and `get_weather_forecast` tools
- **ADK Agent** — uses Gemini 2.0 Flash to reason over weather data and respond naturally
- **Web App** — FastAPI wrapper with a simple chat UI, deployable to Cloud Run

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Docker | Latest |
| gcloud CLI | Latest |
| Google Cloud project | With billing enabled |

---

## Setup

### 1. Get API keys

**OpenWeatherMap (free):**
1. Sign up at https://openweathermap.org/api
2. Go to API Keys → copy your default key
3. Wait ~10 minutes for it to activate

**Google AI (Gemini):**
1. Go to https://aiskudio.google.com/
2. Create an API key

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your keys
```

### 3. Install dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Run Locally

```bash
bash scripts/run_local.sh
```

Open http://localhost:8080 and try:
- *"What's the weather in Mumbai?"*
- *"Give me a 3-day forecast for London"*
- *"Is it a good day to go outside in Tokyo?"*

---

## Deploy to Cloud Run

### 1. Edit deploy script

Open `scripts/deploy.sh` and set:
```bash
PROJECT_ID="track-2-connecting-tools"
REGION="us-central1"
OPENWEATHER_API_KEY="your-openweathermap-key"
GOOGLE_API_KEY="your-google-ai-key"
```

### 2. Authenticate and deploy

```bash
gcloud auth login
gcloud auth configure-docker
bash scripts/deploy.sh
```

The script will output your **Cloud Run URL** — this is your submission link.

### 3. Verify

```bash
curl https://your-agent-url.run.app/health
# → {"status":"healthy","service":"weather-agent"}
```

---

## Project Structure

```
weather-agent/
├── mcp_server/
│   ├── __init__.py
│   └── server.py          # MCP server with weather tools
├── agent/
│   ├── __init__.py
│   └── agent.py           # ADK agent connecting to MCP
├── scripts/
│   ├── deploy.sh          # Cloud Run deployment script
│   └── run_local.sh       # Local dev runner
├── main.py                # FastAPI web app (Cloud Run entry point)
├── Dockerfile             # Agent service container
├── Dockerfile.mcp         # MCP server container
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## MCP Tools Exposed

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_current_weather` | Current conditions for any city | `city`, `units` |
| `get_weather_forecast` | 1–5 day forecast | `city`, `days`, `units` |

---

## Submission

Submit:
1. **Cloud Run URL** — `https://weather-agent-xxxxx.run.app`
2. **GitHub repo URL** — push this project to a public repo

---

## Cleanup (avoid charges)

```bash
gcloud run services delete weather-agent --region us-central1
gcloud run services delete weather-mcp-server --region us-central1
```
