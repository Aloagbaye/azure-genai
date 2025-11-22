#!/usr/bin/env bash

# ==========================================================
# Cosmos DB (Gremlin API) Setup Script
# ==========================================================

RESOURCE_GROUP="azure-genai"
COSMOS_ACCOUNT="genai-graph"
LOCATION="canadacentral"
DB_NAME="knowledge"
GRAPH_NAME="tutorialgraph"

echo "🔹 Creating Cosmos DB account..."
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --kind GlobalDocumentDB \
  --capabilities EnableGremlin \
  --locations regionName=$LOCATION

echo "🔹 Creating Gremlin database..."
az cosmosdb gremlin database create \
  --account-name $COSMOS_ACCOUNT \
  --name $DB_NAME \
  --resource-group $RESOURCE_GROUP

echo "🔹 Creating Gremlin graph..."
az cosmosdb gremlin graph create \
  --account-name $COSMOS_ACCOUNT \
  --database-name $DB_NAME \
  --name $GRAPH_NAME \
  --resource-group $RESOURCE_GROUP \
  --partition-key-path "//pk"

echo "🔹 Fetching Cosmos DB endpoint and key..."
COSMOS_ENDPOINT=$(az cosmosdb show \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --query "documentEndpoint" -o tsv)

COSMOS_KEY=$(az cosmosdb keys list \
  --name $COSMOS_ACCOUNT \
  --resource-group $RESOURCE_GROUP \
  --type keys \
  --query "primaryMasterKey" -o tsv)

echo ""
echo "✅ Cosmos DB setup complete."
echo "📌 COSMOS_ENDPOINT=$COSMOS_ENDPOINT"
echo "📌 COSMOS_KEY=$COSMOS_KEY"