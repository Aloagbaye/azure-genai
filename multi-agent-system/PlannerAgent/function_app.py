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

