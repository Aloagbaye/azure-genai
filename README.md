# Azure GenAI

A FastAPI-based application that integrates Azure OpenAI (GPT-4o) and Azure AI Search to provide chat, embedding, and RAG (Retrieval Augmented Generation) capabilities.

## Features

- **Chat API**: Direct chat interface with GPT-4o
- **Ask API**: RAG-powered Q&A that searches documents and provides context-aware answers
- **Embedding API**: Generate embeddings using Azure OpenAI's text-embedding-3-small model
- **Azure AI Search Integration**: Vector search capabilities for semantic document retrieval

## Prerequisites

- Python 3.8+
- Azure CLI installed and configured
- Azure subscription with access to:
  - Azure OpenAI Service
  - Azure AI Search

## Setup

### 1. Azure Resource Setup

Run the setup script to create and configure Azure resources:

```bash
cd api/services
bash setup_azure_openai.sh
```

This script will:
- Create an Azure resource group (`azure-genai`)
- Create an Azure OpenAI resource (`genai-openai`)
- Deploy GPT-4o model (`gpt4o` deployment)
- Deploy text-embedding-3-small model (`embedding-small` deployment)
- Create an Azure AI Search service (`soel-genai-search`)

**Note**: The script will prompt you to log in to Azure. Make sure you have the necessary permissions.

### 2. Environment Variables

Create a `.env` file in the project root with the following variables:

```env
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=embedding-small
AZURE_SEARCH_ENDPOINT=https://your-search-service.search.windows.net
AZURE_SEARCH_API_KEY=your-search-api-key
AZURE_SEARCH_INDEX_NAME=docs-index
```

You can retrieve these values from:
- **Azure OpenAI Endpoint & API Key**: Run `az cognitiveservices account keys list --name genai-openai --resource-group azure-genai`
- **Azure AI Search Endpoint & API Key**: Available in the Azure Portal under your search service

### 3. Create Search Index

After the Azure AI Search service is created, you need to create the search index. The index schema is defined in `infrastructure/ai_search/index-schema.json`.

You can create the index using the Azure Portal or Azure CLI:

```bash
az search index create \
  --service-name soel-genai-search \
  --resource-group azure-genai \
  --index-name docs-index \
  --body @infrastructure/ai_search/index-schema.json
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

Start the FastAPI server:

```bash
uvicorn api.main:app --reload
```

The API will be available at `http://localhost:8000`

API documentation (Swagger UI) is available at `http://localhost:8000/docs`

## API Endpoints

### POST `/chat`
Direct chat with GPT-4o.

**Request:**
```json
{
  "user_input": "Hello, how are you?"
}
```

**Response:**
```json
{
  "response": "I'm doing well, thank you for asking!"
}
```

### POST `/ask`
RAG-powered Q&A that searches documents and provides context-aware answers.

**Request:**
```json
{
  "query": "What is the main topic of the documentation?"
}
```

**Response:**
```json
{
  "response": "Based on the documentation..."
}
```

### POST `/embed`
Generate embeddings for text.

**Request:**
```json
{
  "text": "Your text to embed"
}
```

**Response:**
```json
{
  "embedding": [0.123, 0.456, ...]
}
```

## Project Structure

```
azure-genai/
├── api/
│   ├── main.py                 # FastAPI application entry point
│   ├── routers/                # API route handlers
│   │   ├── chat.py            # Chat endpoint
│   │   ├── ask.py             # RAG Q&A endpoint
│   │   └── embed.py           # Embedding endpoint
│   ├── services/              # Business logic
│   │   ├── aoai_client.py     # Azure OpenAI client
│   │   ├── embedding_client.py # Embedding service
│   │   ├── search_engine.py   # Azure AI Search integration
│   │   └── setup_azure_openai.sh # Azure setup script
│   └── utils/                 # Utility functions
│       ├── chunker.py         # Document chunking
│       └── chunking.py        # Chunking utilities
├── infrastructure/
│   └── ai_search/
│       └── index-schema.json  # Azure AI Search index schema
├── scripts/                   # Utility scripts
└── requirements.txt           # Python dependencies
```

## Technologies Used

- **FastAPI**: Modern Python web framework
- **Azure OpenAI**: GPT-4o and text-embedding-3-small models
- **Azure AI Search**: Vector search and document retrieval
- **Python-dotenv**: Environment variable management
- **Unstructured**: Document processing
- **NLTK**: Natural language processing utilities

## License

See LICENSE file for details.
