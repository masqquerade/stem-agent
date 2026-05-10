import os
from src.llm.api.llm_client import LLMClient
from src.llm.tools.tools import BUILTIN_TOOLS
from src.llm.workflows.helpers.sanitizer import sanitize_payload

def test_web_search():
    client = LLMClient(api_key=os.environ.get("API_KEY"))
    tools = [BUILTIN_TOOLS["web_search"]]
    
    context = [
        {"role": "user", "content": "Search the web for the latest news on Llama 4."}
    ]
    
    response, record = client.call_agentic(context, label="Test Web Search", tools=tools, temperature=0.3)
    
    print("Has tool calls:", record.has_tool_calls)
    for item in response.output:
        if item.type == "web_search_call":
            args = sanitize_payload(item)
            print("Sanitized args:", args)

if __name__ == "__main__":
    test_web_search()
