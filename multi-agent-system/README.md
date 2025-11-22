# Multi-Agent System

This directory contains the implementation of a multi-agent task automation system using Azure Functions and Durable Functions.

## Structure

```
multi-agent-system/
├── PlannerAgent/          # Breaks tasks into actionable steps
│   └── function_app.py
├── WorkerAgent/           # Retrieves information using RAG
│   └── function_app.py
├── ExecutorAgent/         # Performs actions based on instructions
│   └── function_app.py
├── ReviewerAgent/         # Validates output and enforces Responsible AI
│   └── function_app.py
├── Orchestrator/          # Coordinates all agents using Durable Functions
│   └── function_app.py
├── host.json              # Azure Functions host configuration
├── requirements.txt       # Python dependencies
├── local.settings.json.example  # Local development settings template
└── README.md             # This file
```

## Deployment Options

### Option 1: Single Function App (Recommended)
Deploy all agents as separate functions within one Azure Function App. This is more cost-effective and easier to manage.

1. Create a single `function_app.py` that imports all agent functions
2. Deploy once to Azure

### Option 2: Separate Function Apps
Deploy each agent as a separate Azure Function App. This provides better isolation but requires more management.

1. Deploy each folder as a separate function app
2. Update function URLs in the Orchestrator's environment variables

## Setup

1. Copy `local.settings.json.example` to `local.settings.json` and fill in your Azure credentials
2. Install dependencies: `pip install -r requirements.txt`
3. Install Azure Functions Core Tools: `npm install -g azure-functions-core-tools@4`
4. Run locally: `func start`
5. Deploy to Azure Functions (see main tutorial)

## Testing

See the main tutorial document (`module_5_multi_agent_workflows.md`) for testing instructions.

### Quick Test

```bash
# Test Planner Agent
curl -X POST http://localhost:7071/api/planner \
  -H "Content-Type: application/json" \
  -d '{"task": "Research Azure OpenAI pricing and create a summary"}'

# Test Full Orchestration
curl -X POST http://localhost:7071/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"task": "Research Azure OpenAI pricing and create a summary document"}'
```

