import json
import os

from dotenv import load_dotenv

from src.llm.agents.stem_agent import StemAgent, Target

load_dotenv()

def main():
    target = Target(
        problem_class="Deep Research / System Architecture",
        initial_task_description=(
            """
    Conduct a rigorous, up-to-date comparative analysis of the API pricing and performance trade-offs for three leading frontier LLMs (e.g., GPT-4o, Claude 3.5 Sonnet, and Gemini 1.5 Pro) as of 2026. You must use web search to find their exact per-million-token input/output costs, context caching discount rates, and their latest HumanEval benchmark scores. Next, use the code interpreter to simulate a monthly production workload consisting of 250 million input tokens (assuming a 65% cache hit rate) and 50 million output tokens. Calculate the exact monthly operational cost for each model. Finally, calculate the 'Cost per HumanEval percentage point' and construct a structured recommendation matrix advising a high-volume coding startup on the optimal model. Output the entire report directly in your response; do not save or write to any local files.
            """
        )
    )

    agent = StemAgent(os.getenv("API_KEY"), target)

    result, scoring = agent.run(3)

    print(f"[FINAL]: Result scoring: {json.dumps(scoring, indent=2)}")

    print(result)

if __name__ == "__main__":
    main()