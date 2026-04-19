import os

from dotenv import load_dotenv

from src.llm.agents.stem_agent import StemAgent, Target

load_dotenv()

def main():
    target = Target(
        problem_class="Quality Assurance for Code",
        initial_task_description="Review my last commit to the codebase in main branch and find possible vulnerabilities."
    )

    stem_agent = StemAgent(os.getenv("API_KEY"), target)

    response = stem_agent.build_scoring_function()

    print(response.output[1].content[0].text)

if __name__ == "__main__":
    main()