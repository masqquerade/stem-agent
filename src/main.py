import os
from os.path import isfile, join

from dotenv import load_dotenv

from src.db.db import VectorDatabase, Document
from src.llm.agents.stem_agent import StemAgent, Target

from os import listdir

load_dotenv()

def handle_knowledge(path: str, db: VectorDatabase):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for f in files:
        with open(join(path, f), "r") as file:
            content = file.read()
            doc = Document(content=content, source=f)
            db.add([doc])


def main():
    api_key = os.getenv("API_KEY")

    db = VectorDatabase()

    print("=== STEM Agent ===")
    problem_class = input("Problem class: ").strip()
    task = input("Initial task: ").strip()
    knowledge_base_path = input("Knowledge base path (leave empty to skip): ").strip()

    if knowledge_base_path:
        handle_knowledge(knowledge_base_path, db)

    agent = StemAgent(api_key, Target(problem_class=problem_class, initial_task_description=task), db=db)

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
