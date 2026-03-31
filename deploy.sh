#!/bin/bash
set -e

PROJECT_ID="track-2-connecting-tools"
REGION="us-central1"
OPENWEATHER_API_KEY="your-api-key-here"
GOOGLE_API_KEY="your-google-api-key"

REPO="gcr.io/${PROJECT_ID}"
MCP_IMAGE="${REPO}/weather-mcp-server"
AGENT_IMAGE="${REPO}/weather-agent"
MCP_SERVICE="weather-mcp-server"
AGENT_SERVICE="weather-agent"

echo "▶ Configuring project: ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"

echo "▶ Enabling required APIs..."
gcloud services enable run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  --quiet

echo "▶ Building MCP server image..."
docker build -f Dockerfile.mcp -t "${MCP_IMAGE}" .

echo "▶ Pushing MCP server image..."
docker push "${MCP_IMAGE}"

echo "▶ Deploying MCP server to Cloud Run..."
gcloud run deploy "${MCP_SERVICE}" \
  --image "${MCP_IMAGE}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-env-vars "OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 5 \
  --quiet

MCP_URL=$(gcloud run services describe "${MCP_SERVICE}" \
  --platform managed \
  --region "${REGION}" \
  --format "value(status.url)")

MCP_SERVER_URL="${MCP_URL}/mcp"
echo "✅ MCP server deployed at: ${MCP_SERVER_URL}"

echo "▶ Building agent image..."
docker build -f Dockerfile -t "${AGENT_IMAGE}" .

echo "▶ Pushing agent image..."
docker push "${AGENT_IMAGE}"

echo "▶ Deploying agent to Cloud Run..."
gcloud run deploy "${AGENT_SERVICE}" \
  --image "${AGENT_IMAGE}" \
  --platform managed \
  --region "${REGION}" \
  --allow-unauthenticated \
  --set-env-vars "MCP_SERVER_URL=${MCP_SERVER_URL},GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
  --memory 1Gi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --quiet

AGENT_URL=$(gcloud run services describe "${AGENT_SERVICE}" \
  --platform managed \
  --region "${REGION}" \
  --format "value(status.url)")

echo ""
echo "════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE"
echo "════════════════════════════════════════════"
echo "🌤  Agent URL (submit this): ${AGENT_URL}"
echo "🔧  MCP Server URL:          ${MCP_SERVER_URL}"
echo "════════════════════════════════════════════"
