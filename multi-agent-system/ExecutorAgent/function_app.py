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

