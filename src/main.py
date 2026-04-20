import os

from dotenv import load_dotenv

from src.llm.agents.stem_agent import StemAgent, Target

load_dotenv()

def main():
    target = Target(
        problem_class="Code Generation",
        initial_task_description="Read the file /home/xgod/PycharmProjects/jb_stem/src/llm/api/llm_client.py and write a complete test suite for it using pytest. Tests should cover normal behavior, edge cases, and error handling. Save the result to /home/xgod/PycharmProjects/jb_stem/tests/test_llm_client.py"
    )

    stem_agent = StemAgent(os.getenv("API_KEY"), target)

    response = stem_agent.build_scoring_function()

    response = stem_agent.run_baseline()
    print(response)

    scoring = stem_agent.score_output(response)
    print(scoring)

if __name__ == "__main__":
    main()