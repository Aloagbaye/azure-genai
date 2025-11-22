# 🤖 Module 5 — Multi-Agent Workflows on Azure

This tutorial covers building multi-agent automation systems using Azure services, including Azure Functions, Logic Apps, Durable Functions, and Azure OpenAI Assistants API.

---

## 📚 Table of Contents

1. [Introduction to Agent Architectures](#introduction-to-agent-architectures)
2. [Azure Services for Agents](#azure-services-for-agents)
3. [Building a Multi-Agent Task Automation System](#building-a-multi-agent-task-automation-system)
4. [Hands-On Implementation](#hands-on-implementation)
5. [Advanced Patterns](#advanced-patterns)

---

## 🎯 Introduction to Agent Architectures

### What is an AI Agent?

An AI agent is an autonomous system that:
- **Perceives** its environment through inputs
- **Decides** what actions to take using an LLM
- **Acts** by calling tools/functions
- **Remembers** past interactions and context

### Core Components

#### 1. **LLM as an Agent**
The LLM serves as the "brain" that:
- Interprets user requests
- Plans sequences of actions
- Makes decisions based on context
- Generates responses

#### 2. **Tools**
Tools are functions the agent can call:
- **RAG Search**: Query knowledge bases
- **Code Execution**: Run Python scripts
- **API Calls**: Interact with external services
- **Database Queries**: Retrieve structured data
- **File Operations**: Read/write files

#### 3. **Memory**
Agents need memory to:
- **Short-term**: Current conversation context
- **Long-term**: Past interactions, user preferences
- **Episodic**: Specific events and outcomes
- **Semantic**: Learned patterns and knowledge

### Agent Types

1. **Reactive Agents**: Respond to immediate inputs
2. **Deliberative Agents**: Plan before acting
3. **Hybrid Agents**: Combine reactive and planning capabilities

---

## 🏗️ Azure Services for Agents

### 1. Azure Functions

**Use Case**: Stateless, event-driven agent execution

**Features**:
- Serverless compute
- HTTP triggers, queue triggers, timer triggers
- Built-in scaling
- Pay-per-execution

**Example Use Case**: Worker agent that processes tasks from a queue

### 2. Logic Apps

**Use Case**: Visual workflow orchestration

**Features**:
- Low-code/no-code workflows
- 400+ connectors
- Built-in error handling
- State management

**Example Use Case**: Routing tasks between agents based on conditions

### 3. Durable Functions

**Use Case**: Long-running, stateful agent orchestration

**Features**:
- Stateful workflows
- Checkpointing and replay
- Fan-out/fan-in patterns
- Human interaction support

**Example Use Case**: Multi-agent task automation with complex workflows

### 4. Azure OpenAI Assistants API

**Use Case**: Managed agent framework with built-in tools

**Features**:
- Thread management
- Built-in tool calling
- File search capabilities
- Code interpreter
- Function calling

**Example Use Case**: Pre-built agent with RAG and code execution

---

## 🛠️ Building a Multi-Agent Task Automation System

### System Architecture

```
User Request
    ↓
[Planner Agent] → Breaks task into steps
    ↓
[Durable Functions Orchestrator] → Coordinates workflow
    ↓
    ├─→ [Worker Agent] → Retrieves info (RAG)
    ├─→ [Executor Agent] → Performs actions
    └─→ [Reviewer Agent] → Validates & enforces RAI
    ↓
Response to User
```

### Agent Roles

#### 1. **Planner Agent**
- **Input**: User task description
- **Output**: Structured plan with steps
- **Tools**: None (pure reasoning)
- **Example**: "Break down 'Research Azure OpenAI pricing' into steps"

#### 2. **Worker Agent**
- **Input**: Specific information need
- **Output**: Retrieved information
- **Tools**: RAG search, web search, database queries
- **Example**: "Find Azure OpenAI pricing information"

#### 3. **Executor Agent**
- **Input**: Action to perform
- **Output**: Action result
- **Tools**: API calls, code execution, file operations
- **Example**: "Generate a summary document"

#### 4. **Reviewer Agent**
- **Input**: Agent output
- **Output**: Validation result + RAI compliance check
- **Tools**: Content moderation, fact-checking
- **Example**: "Review response for accuracy and safety"

---

## 💻 Hands-On Implementation

### Prerequisites

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Install Python dependencies
pip install azure-functions azure-durable-functions openai python-dotenv
```

### Step 1: Set Up Project Structure

```
multi-agent-system/
├── PlannerAgent/
│   └── function_app.py
├── WorkerAgent/
│   └── function_app.py
├── ExecutorAgent/
│   └── function_app.py
├── ReviewerAgent/
│   └── function_app.py
├── Orchestrator/
│   └── function_app.py
├── requirements.txt
└── .env
```

### Step 2: Create the Planner Agent

**File**: `PlannerAgent/function_app.py`

```python
import azure.functions as func
import logging
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

app = func.FunctionApp()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.route(route="planner", auth_level=func.AuthLevel.FUNCTION)
def planner_agent(req: func.HttpRequest) -> func.HttpResponse:
    """
    Planner Agent: Breaks down tasks into actionable steps
    """
    logging.info('Planner Agent triggered')
    
    try:
        req_body = req.get_json()
        task = req_body.get('task', '')
        
        if not task:
            return func.HttpResponse(
                "Task is required",
                status_code=400
            )
        
        # Use LLM to create a plan
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {
                    "role": "system",
                    "content": """You are a task planning agent. Break down user tasks into 
                    clear, actionable steps. Return a JSON array of steps, each with:
                    - step_number: int
                    - description: string
                    - agent_type: "worker" | "executor" | "reviewer"
                    - required_info: string (what information is needed)
                    """
                },
                {
                    "role": "user",
                    "content": f"Break down this task into steps: {task}"
                }
            ],
            temperature=0.3
        )
        
        plan_text = response.choices[0].message.content
        
        # Extract JSON from response
        try:
            # Try to parse if it's pure JSON
            plan = json.loads(plan_text)
        except:
            # Extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```json\n(.*?)\n```', plan_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group(1))
            else:
                # Fallback: create simple plan
                plan = [{
                    "step_number": 1,
                    "description": task,
                    "agent_type": "worker",
                    "required_info": task
                }]
        
        return func.HttpResponse(
            json.dumps({"plan": plan, "task": task}),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error in planner agent: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
```

### Step 3: Create the Worker Agent (RAG)

**File**: `WorkerAgent/function_app.py`

```python
import azure.functions as func
import logging
import os
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
import json

load_dotenv()

app = func.FunctionApp()

# Azure OpenAI client
aoai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Azure AI Search client
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

@app.route(route="worker", auth_level=func.AuthLevel.FUNCTION)
def worker_agent(req: func.HttpRequest) -> func.HttpResponse:
    """
    Worker Agent: Retrieves information using RAG
    """
    logging.info('Worker Agent triggered')
    
    try:
        req_body = req.get_json()
        query = req_body.get('query', '')
        
        if not query:
            return func.HttpResponse(
                "Query is required",
                status_code=400
            )
        
        # Perform RAG search
        results = search_client.search(
            search_text=query,
            top=5,
            include_total_count=True
        )
        
        # Extract relevant documents
        documents = []
        for result in results:
            documents.append({
                "content": result.get("content", ""),
                "title": result.get("title", ""),
                "score": result.get("@search.score", 0)
            })
        
        # Generate embedding for query
        embedding_response = aoai_client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            input=query
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Vector search (if using vector fields)
        vector_results = search_client.search(
            search_text="",
            vector_queries=[{
                "vector": query_embedding,
                "k_nearest_neighbors": 3,
                "fields": "embedding"
            }],
            top=3
        )
        
        # Combine results
        all_docs = list(documents)
        for result in vector_results:
            all_docs.append({
                "content": result.get("content", ""),
                "title": result.get("title", ""),
                "score": result.get("@search.score", 0)
            })
        
        # Summarize findings
        context = "\n\n".join([doc["content"] for doc in all_docs[:5]])
        
        summary_response = aoai_client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant. Summarize the retrieved information to answer the query."
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\n\nContext:\n{context}\n\nProvide a concise answer based on the context."
                }
            ],
            temperature=0.3
        )
        
        answer = summary_response.choices[0].message.content
        
        return func.HttpResponse(
            json.dumps({
                "query": query,
                "answer": answer,
                "sources": all_docs[:5],
                "source_count": len(all_docs)
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error in worker agent: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
```

### Step 4: Create the Executor Agent

**File**: `ExecutorAgent/function_app.py`

```python
import azure.functions as func
import logging
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import subprocess
import tempfile

load_dotenv()

app = func.FunctionApp()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.route(route="executor", auth_level=func.AuthLevel.FUNCTION)
def executor_agent(req: func.HttpRequest) -> func.HttpResponse:
    """
    Executor Agent: Performs actions based on instructions
    """
    logging.info('Executor Agent triggered')
    
    try:
        req_body = req.get_json()
        action = req_body.get('action', '')
        context = req_body.get('context', '')
        
        if not action:
            return func.HttpResponse(
                "Action is required",
                status_code=400
            )
        
        # Use LLM to determine what to execute
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {
                    "role": "system",
                    "content": """You are an execution agent. Based on the action requested,
                    determine what needs to be done. You can:
                    - Generate text/documents
                    - Create summaries
                    - Format data
                    - Perform calculations
                    
                    Return a JSON with:
                    - action_type: "generate" | "calculate" | "format"
                    - result: the output of the action
                    """
                },
                {
                    "role": "user",
                    "content": f"Action: {action}\n\nContext: {context}\n\nExecute this action."
                }
            ],
            temperature=0.3
        )
        
        result_text = response.choices[0].message.content
        
        # Extract JSON
        try:
            result = json.loads(result_text)
        except:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(1))
            else:
                result = {
                    "action_type": "generate",
                    "result": result_text
                }
        
        return func.HttpResponse(
            json.dumps({
                "action": action,
                "result": result,
                "status": "completed"
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error in executor agent: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
```

### Step 5: Create the Reviewer Agent (RAI)

**File**: `ReviewerAgent/function_app.py`

```python
import azure.functions as func
import logging
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json

load_dotenv()

app = func.FunctionApp()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

@app.route(route="reviewer", auth_level=func.AuthLevel.FUNCTION)
def reviewer_agent(req: func.HttpRequest) -> func.HttpResponse:
    """
    Reviewer Agent: Validates output and enforces Responsible AI
    """
    logging.info('Reviewer Agent triggered')
    
    try:
        req_body = req.get_json()
        content = req_body.get('content', '')
        original_task = req_body.get('task', '')
        
        if not content:
            return func.HttpResponse(
                "Content is required",
                status_code=400
            )
        
        # RAI Review
        rai_response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            messages=[
                {
                    "role": "system",
                    "content": """You are a Responsible AI reviewer. Evaluate content for:
                    1. Accuracy: Is the information correct?
                    2. Safety: Does it contain harmful content?
                    3. Bias: Are there any biases present?
                    4. Completeness: Does it address the task?
                    5. Compliance: Does it follow guidelines?
                    
                    Return JSON with:
                    - approved: boolean
                    - accuracy_score: float (0-1)
                    - safety_score: float (0-1)
                    - issues: array of strings
                    - recommendations: array of strings
                    """
                },
                {
                    "role": "user",
                    "content": f"Task: {original_task}\n\nContent to review:\n{content}"
                }
            ],
            temperature=0.1
        )
        
        review_text = rai_response.choices[0].message.content
        
        # Extract JSON
        try:
            review = json.loads(review_text)
        except:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', review_text, re.DOTALL)
            if json_match:
                review = json.loads(json_match.group(1))
            else:
                review = {
                    "approved": True,
                    "accuracy_score": 0.8,
                    "safety_score": 1.0,
                    "issues": [],
                    "recommendations": []
                }
        
        return func.HttpResponse(
            json.dumps({
                "content": content,
                "review": review,
                "approved": review.get("approved", True)
            }),
            mimetype="application/json",
            status_code=200
        )
        
    except Exception as e:
        logging.error(f"Error in reviewer agent: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            mimetype="application/json",
            status_code=500
        )
```

### Step 6: Create Durable Functions Orchestrator

**File**: `Orchestrator/function_app.py`

```python
import azure.functions as func
import azure.durable_functions as df
import logging
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Get function URLs (adjust based on your deployment)
PLANNER_URL = os.getenv("PLANNER_FUNCTION_URL", "http://localhost:7071/api/planner")
WORKER_URL = os.getenv("WORKER_FUNCTION_URL", "http://localhost:7071/api/worker")
EXECUTOR_URL = os.getenv("EXECUTOR_FUNCTION_URL", "http://localhost:7071/api/executor")
REVIEWER_URL = os.getenv("REVIEWER_FUNCTION_URL", "http://localhost:7071/api/reviewer")

@app.route(route="orchestrate", auth_level=func.AuthLevel.FUNCTION)
async def http_start(req: func.HttpRequest, starter: str) -> func.HttpResponse:
    """
    HTTP trigger to start the orchestration
    """
    client = df.DurableOrchestrationClient(starter)
    
    try:
        req_body = req.get_json()
        task = req_body.get('task', '')
        
        if not task:
            return func.HttpResponse(
                "Task is required",
                status_code=400
            )
        
        instance_id = await client.start_new("multi_agent_orchestrator", None, {"task": task})
        
        return client.create_check_status_response(req, instance_id)
        
    except Exception as e:
        logging.error(f"Error starting orchestration: {str(e)}")
        return func.HttpResponse(
            f"Error: {str(e)}",
            status_code=500
        )

@app.orchestration_trigger(context_name="context")
def multi_agent_orchestrator(context: df.DurableOrchestrationContext):
    """
    Main orchestration function that coordinates all agents
    """
    task = context.get_input()["task"]
    
    # Step 1: Planner Agent - Create plan
    logging.info(f"Step 1: Planning for task: {task}")
    plan_result = yield context.call_activity("call_planner_agent", task)
    plan = plan_result.get("plan", [])
    
    results = []
    
    # Step 2: Execute each step in the plan
    for step in plan:
        step_num = step.get("step_number", 0)
        description = step.get("description", "")
        agent_type = step.get("agent_type", "worker")
        required_info = step.get("required_info", "")
        
        logging.info(f"Step {step_num}: Executing {agent_type} agent - {description}")
        
        if agent_type == "worker":
            # Worker Agent - Retrieve information
            worker_result = yield context.call_activity(
                "call_worker_agent",
                {"query": required_info or description}
            )
            results.append({
                "step": step_num,
                "type": "worker",
                "result": worker_result
            })
            
        elif agent_type == "executor":
            # Executor Agent - Perform action
            executor_result = yield context.call_activity(
                "call_executor_agent",
                {
                    "action": description,
                    "context": str(results)  # Pass previous results as context
                }
            )
            results.append({
                "step": step_num,
                "type": "executor",
                "result": executor_result
            })
    
    # Step 3: Reviewer Agent - Review final output
    logging.info("Step 3: Reviewing output")
    final_content = "\n".join([str(r["result"]) for r in results])
    
    review_result = yield context.call_activity(
        "call_reviewer_agent",
        {
            "content": final_content,
            "task": task
        }
    )
    
    # Return final result
    return {
        "task": task,
        "plan": plan,
        "results": results,
        "review": review_result,
        "approved": review_result.get("approved", True)
    }

@app.activity_trigger(input_name="task")
def call_planner_agent(task: str):
    """Call the Planner Agent"""
    response = requests.post(
        PLANNER_URL,
        json={"task": task},
        headers={"Content-Type": "application/json"}
    )
    return response.json()

@app.activity_trigger(input_name="input_data")
def call_worker_agent(input_data: dict):
    """Call the Worker Agent"""
    response = requests.post(
        WORKER_URL,
        json=input_data,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

@app.activity_trigger(input_name="input_data")
def call_executor_agent(input_data: dict):
    """Call the Executor Agent"""
    response = requests.post(
        EXECUTOR_URL,
        json=input_data,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

@app.activity_trigger(input_name="input_data")
def call_reviewer_agent(input_data: dict):
    """Call the Reviewer Agent"""
    response = requests.post(
        REVIEWER_URL,
        json=input_data,
        headers={"Content-Type": "application/json"}
    )
    return response.json()
```

### Step 7: Environment Configuration

**File**: `.env`

```env
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_API_VERSION=2024-08-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt4o
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=embedding-small

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-key
AZURE_SEARCH_INDEX_NAME=docs-index

# Function URLs (update after deployment)
PLANNER_FUNCTION_URL=https://your-function-app.azurewebsites.net/api/planner
WORKER_FUNCTION_URL=https://your-function-app.azurewebsites.net/api/worker
EXECUTOR_FUNCTION_URL=https://your-function-app.azurewebsites.net/api/executor
REVIEWER_FUNCTION_URL=https://your-function-app.azurewebsites.net/api/reviewer
```

### Step 8: Requirements

**File**: `requirements.txt`

```
azure-functions
azure-durable-functions
azure-identity
azure-search-documents
openai
python-dotenv
requests
```

---

## 🚀 Deployment

### Deploy to Azure Functions

```bash
# Login to Azure
az login

# Create Function App
az functionapp create \
  --resource-group azure-genai \
  --consumption-plan-location canadaeast \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --name your-multi-agent-app \
  --storage-account yourstorageaccount

# Deploy functions
func azure functionapp publish your-multi-agent-app

# Set environment variables
az functionapp config appsettings set \
  --name your-multi-agent-app \
  --resource-group azure-genai \
  --settings \
    AZURE_OPENAI_ENDPOINT="..." \
    AZURE_OPENAI_API_KEY="..." \
    # ... other settings
```

---

## 🧪 Testing

### Test Individual Agents

```bash
# Test Planner
curl -X POST http://localhost:7071/api/planner \
  -H "Content-Type: application/json" \
  -d '{"task": "Research Azure OpenAI pricing and create a summary"}'

# Test Worker
curl -X POST http://localhost:7071/api/worker \
  -H "Content-Type: application/json" \
  -d '{"query": "Azure OpenAI pricing"}'

# Test Executor
curl -X POST http://localhost:7071/api/executor \
  -H "Content-Type: application/json" \
  -d '{"action": "Create a summary", "context": "..."}'

# Test Reviewer
curl -X POST http://localhost:7071/api/reviewer \
  -H "Content-Type: application/json" \
  -d '{"content": "...", "task": "..."}'
```

### Test Full Orchestration

```bash
curl -X POST http://localhost:7071/api/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"task": "Research Azure OpenAI pricing and create a summary document"}'
```

---

## 🎓 Advanced Patterns

### Pattern 1: Agent Teams with Specialization

```python
# Specialized agents for different domains
AGENT_TEAMS = {
    "technical": ["tech_worker", "code_executor"],
    "business": ["business_worker", "analyst_executor"],
    "research": ["research_worker", "writer_executor"]
}

def route_to_team(task: str) -> str:
    # Use LLM to determine team
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Classify task into: technical, business, or research"},
            {"role": "user", "content": task}
        ]
    )
    return response.choices[0].message.content.lower()
```

### Pattern 2: Human-in-the-Loop

```python
@app.orchestration_trigger(context_name="context")
def human_in_loop_orchestrator(context: df.DurableOrchestrationContext):
    task = context.get_input()["task"]
    
    # Get approval before execution
    approval = yield context.call_activity("get_human_approval", task)
    
    if approval.get("approved"):
        result = yield context.call_activity("execute_task", task)
    else:
        result = {"status": "cancelled", "reason": approval.get("reason")}
    
    return result
```

### Pattern 3: Retry with Backoff

```python
import time

def call_agent_with_retry(agent_url, payload, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(agent_url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise e
    return None
```

### Pattern 4: Using Azure OpenAI Assistants API

```python
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-08-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Create assistant with tools
assistant = client.beta.assistants.create(
    name="Multi-Agent Assistant",
    instructions="You are a helpful assistant that can search documents and execute code.",
    model="gpt-4o",
    tools=[
        {"type": "code_interpreter"},
        {"type": "file_search"}
    ]
)

# Create thread
thread = client.beta.threads.create()

# Add message
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Research Azure OpenAI and create a summary"
)

# Run assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Poll for completion
while run.status in ["queued", "in_progress"]:
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    time.sleep(1)

# Get messages
messages = client.beta.threads.messages.list(thread_id=thread.id)
```

---

## 📊 Monitoring and Observability

### Application Insights Integration

```python
from opencensus.ext.azure.log_exporter import AzureLogHandler
import logging

logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
))

# Log agent activities
logger.info("Planner agent executed", extra={
    "custom_dimensions": {
        "agent": "planner",
        "task": task,
        "steps_generated": len(plan)
    }
})
```

### Custom Metrics

```python
from opencensus.ext.azure import metrics_exporter

exporter = metrics_exporter.new_metrics_exporter(
    connection_string=os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
)

# Track agent performance
exporter.export_metrics([{
    "name": "agent_execution_time",
    "value": execution_time,
    "tags": {"agent": "worker"}
}])
```

---

## ✅ Best Practices

1. **Error Handling**: Always wrap agent calls in try-except blocks
2. **Timeouts**: Set appropriate timeouts for agent calls
3. **Idempotency**: Make agents idempotent where possible
4. **Logging**: Log all agent decisions and actions
5. **Security**: Use managed identities and secure key storage
6. **Cost Management**: Monitor token usage and optimize prompts
7. **Testing**: Test each agent independently before integration
8. **Documentation**: Document agent capabilities and limitations

---

## 🎯 Summary

In this module, you learned:

- ✅ Agent architectures and components
- ✅ Azure services for building agents (Functions, Logic Apps, Durable Functions)
- ✅ Building a multi-agent system with specialized roles
- ✅ Implementing RAG in worker agents
- ✅ Enforcing Responsible AI with reviewer agents
- ✅ Orchestrating complex workflows with Durable Functions
- ✅ Advanced patterns for production systems

**Next Steps**:
- Deploy your multi-agent system to Azure
- Add monitoring and observability
- Implement additional agent types
- Experiment with Azure OpenAI Assistants API
- Build domain-specific agent teams

---

## 📚 Additional Resources

- [Azure Functions Documentation](https://docs.microsoft.com/azure/azure-functions/)
- [Durable Functions Patterns](https://docs.microsoft.com/azure/azure-functions/durable/durable-functions-overview)
- [Azure OpenAI Assistants API](https://learn.microsoft.com/azure/ai-services/openai/how-to/assistant)
- [Responsible AI Guidelines](https://www.microsoft.com/ai/responsible-ai)

