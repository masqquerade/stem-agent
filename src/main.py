import json
import os

from dotenv import load_dotenv

from src.llm.agents.stem_agent import StemAgent, Target

load_dotenv()

def main():
    target = Target(
        problem_class="Deep Research",
        initial_task_description=(
            "Compare the latency, infrastructure cost, and contextual accuracy trade-offs of using sparse-dense hybrid retrieval (e.g., Splade + HNSW) in a RAG pipeline versus LoRA fine-tuning for adapting open-weights models (like Llama-3) to highly specialized medical terminology. Provide concrete benchmarks published within the last 12 months, analyze infrastructure costs for a deployment handling 1M daily queries, and formulate a rigorous decision matrix for a resource-constrained health-tech startup."
        )
    )

    agent = StemAgent(os.getenv("API_KEY"), target)

    result, scoring = agent.run(3)

    print(f"[FINAL]: Result scoring: {json.dumps(scoring, indent=2)}")

    print(result)

if __name__ == "__main__":
    main()