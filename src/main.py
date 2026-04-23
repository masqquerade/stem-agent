import json
import os

from dotenv import load_dotenv

from src.llm.agents.stem_agent import StemAgent, Target

load_dotenv()

SEP = "-" * 60


def main():
    target = Target(
        problem_class="Technical Research",
        initial_task_description=(
            "Research and compare the three most widely adopted vector databases (e.g. "
            "Pinecone, Weaviate, Qdrant, Milvus, Chroma) as of 2025. For each, cover: "
            "indexing algorithm and ANN method used, scalability limits and deployment model "
            "(managed vs self-hosted), benchmark performance on recall vs latency tradeoffs, "
            "pricing model, and known production failure modes or limitations. Conclude with "
            "a concrete recommendation matrix: which to use for each of these scenarios — "
            "startup MVP, high-throughput production RAG, on-prem air-gapped deployment."
        )
    )

    agent = StemAgent(os.getenv("API_KEY"), target)

    # --- PHASE 0: PREPARATION ---

    print(SEP)
    print("STEP 1: Building scoring function...")
    scoring_function = agent.build_scoring_function()
    print(f"  => {len(scoring_function)} questions generated")
    for q in scoring_function:
        print(f"     [{q['id']}] {q['question']}")

    print(SEP)
    print("STEP 2: Running baseline...")
    baseline_output = agent.run_baseline()
    print(f"  => Output ({len(baseline_output)} chars):\n{baseline_output[:300]}...")

    print(SEP)
    print("STEP 3: Scoring baseline...")
    agent.baseline_scoring = agent.score_output(baseline_output)
    print(f"  => Scores: {json.dumps(agent.baseline_scoring, indent=2)}")

    print(SEP)
    print("STEP 4: Building test sample...")
    agent._build_test_sample()
    print(f"  => {len(agent.test_sample)} tasks generated")
    for t in agent.test_sample:
        print(f"     [{t['task_id']}] {t['task_description'][:80]}...")

    # --- PHASE 1: GENERATE ---

    print(SEP)
    print("STEP 5: Generating initial config...")
    config = agent._generate(iteration=0)

    agent.current_config = config
    print(f"  => workflow_type:      {config.workflow_type}")
    print(f"  => mutation_strategy:  {config.mutation_strategy}")
    print(f"  => tools:              {config.tools}")
    print(f"  => temperature:        {config.temperature}")
    print(f"  => max_steps:          {config.max_steps}")
    print(f"  => mutation_log:       {config.mutation_log[:200]}...")
    print(config.system_prompt)

    # --- PHASE 2: EVALUATE ---

    print(SEP)
    print("STEP 6: Evaluating config against test sample...")
    scoring = agent._evaluate()
    print(f"  => Scorings: {json.dumps(scoring, indent=2)}")

    print(SEP)
    print("DONE.")

if __name__ == "__main__":
    main()