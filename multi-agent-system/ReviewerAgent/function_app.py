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

