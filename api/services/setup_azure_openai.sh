#!/usr/bin/env bash

# ==========================================================
# Azure OpenAI Setup Script (GPT-4 Deployment)
# ==========================================================

RESOURCE_GROUP="azure-genai"
LOCATION="canadaeast"
AOAI_NAME="genai-openai"

# Deployment
DEPLOYMENT_NAME="gpt4o"
MODEL_NAME="gpt-4o"
MODEL_VERSION="2024-11-20"
MODEL_FORMAT="OpenAI"

echo "🔹 Logging into Azure..."
az login

echo "🔹 Ensuring resource group exists..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

echo "🔹 Creating Azure OpenAI resource (if not exists)..."
az cognitiveservices account create \
    --name $AOAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --kind OpenAI \
    --sku s0 \
    --yes

echo "🔹 Fetching endpoint..."
ENDPOINT=$(az cognitiveservices account show \
    --name $AOAI_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.endpoint" -o tsv)

echo ""
echo "🔹 Azure OpenAI Endpoint:"
echo "$ENDPOINT"
echo ""

echo "🔹 Fetching keys..."
az cognitiveservices account keys list \
    --name $AOAI_NAME \
    --resource-group $RESOURCE_GROUP

echo ""
echo "🔹 Deploying GPT-4o ($MODEL_VERSION)..."
az cognitiveservices account deployment create \
    --resource-group $RESOURCE_GROUP \
    --name $AOAI_NAME \
    --deployment-name $DEPLOYMENT_NAME \
    --model-name $MODEL_NAME \
    --model-version $MODEL_VERSION \
    --model-format $MODEL_FORMAT \
    --sku-capacity 10 \
    --sku-name "Standard"

echo ""
echo "✅ Deployment complete!"
echo "Model deployed as: $DEPLOYMENT_NAME"
echo ""
echo "Use this model name in your Python code:"
echo "    model=\"$DEPLOYMENT_NAME\""

# Variables
EMBEDDING_DEPLOYMENT="embedding-small"
MODEL_NAME="text-embedding-3-small"
MODEL_VERSION="1"
MODEL_FORMAT="OpenAI"

# Deploy
az cognitiveservices account deployment create \
  --resource-group $RESOURCE_GROUP \
  --name $AOAI_NAME \
  --deployment-name $EMBEDDING_DEPLOYMENT \
  --model-name $MODEL_NAME \
  --model-version $MODEL_VERSION \
  --model-format $MODEL_FORMAT \
  --sku-capacity 10 \
  --sku-name Standard

# ==========================================================
# Azure AI Search Setup
# ==========================================================
SEARCH_SERVICE_NAME="genai-search"

echo "🔹 Creating Azure AI Search service..."
az search service create \
    --name $SEARCH_SERVICE_NAME \
    --resource-group $RESOURCE_GROUP \
    --sku basic \
    --location $LOCATION

az search index create \
  --service-name $SEARCH_SERVICE_NAME \
  --resource-group $RESOURCE_GROUP \
  --name docs-index \
  --body @infrastructure/ai_search/index-schema.json

