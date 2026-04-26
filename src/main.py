import os

from dotenv import load_dotenv

from src.llm.agents.stem_agent import StemAgent, Target

load_dotenv()


def main():
    api_key = os.getenv("API_KEY")

    print("=== STEM Agent ===")
    problem_class = input("Problem class: ").strip()
    task = input("Initial task: ").strip()

    agent = StemAgent(api_key, Target(problem_class=problem_class, initial_task_description=task))

    print("\n[*] Running evolution loop...")
    result, scoring = agent.run(3)

    print(f"\n[RESULT] Score: {scoring.get('overall', 0):.2f}")
    print(result)

    while True:
        print("\n---")
        next_task = input("Next task (or 'exit'): ").strip()
        if not next_task or next_task.lower() == "exit":
            break

        result, scoring = agent.execute_task(next_task)
        print(f"\n[RESULT] Score: {scoring.get('overall', 0):.2f}")
        print(result)


if __name__ == "__main__":
    main()
