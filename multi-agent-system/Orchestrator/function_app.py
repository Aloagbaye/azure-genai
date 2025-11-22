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

