#!/usr/bin/env bash
# ==========================================================
# Azure AI Search Index Creation using az rest (corrected)
# ==========================================================
SEARCH_SERVICE_NAME="soel-genai-search"
RESOURCE_GROUP="azure-genai"
API_VERSION="2023-11-01"

# Get admin key
SEARCH_ADMIN_KEY=$(az search admin-key show \
  --resource-group $RESOURCE_GROUP \
  --service-name $SEARCH_SERVICE_NAME \
  --query "primaryKey" -o tsv)

echo "$SEARCH_ADMIN_KEY"

# Ensure schema file exists
SCHEMA_FILE="infrastructure/ai_search/index-schema.json"

# Run az rest with correct headers
echo "🔹 Creating Azure AI Search Index via REST API..."
az rest --method PUT \
  --url "https://$SEARCH_SERVICE_NAME.search.windows.net/indexes/docs-index?api-version=$API_VERSION" \
  --headers "Content-Type=application/json" "api-key=$SEARCH_ADMIN_KEY" \
  --body @$SCHEMA_FILE