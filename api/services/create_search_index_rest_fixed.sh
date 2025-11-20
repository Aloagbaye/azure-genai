#!/usr/bin/env bash

# ==========================================================
# Azure AI Search Index Creation using az rest (corrected)
# ==========================================================

SEARCH_SERVICE_NAME="genai-search-esosa"  # Replace if needed
RESOURCE_GROUP="azure-genai"
API_VERSION="2023-11-01"

# Get admin key
SEARCH_ADMIN_KEY=$(az search admin-key show \
  --resource-group $RESOURCE_GROUP \
  --service-name $SEARCH_SERVICE_NAME \
  --query "primaryKey" -o tsv)

# Ensure schema file exists
SCHEMA_FILE="infrastructure/ai_search/index-schema.json"

# Run az rest with correct headers and --resource flag
echo "🔹 Creating Azure AI Search Index via REST API..."

az rest --method POST \
  --url "https://$SEARCH_SERVICE_NAME.search.windows.net/indexes?api-version=$API_VERSION" \
  --headers "Content-Type=application/json;api-key:$SEARCH_ADMIN_KEY" \
  --resource https://search.azure.com \
  --body @$SCHEMA_FILE