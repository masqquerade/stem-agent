def get_scoring_judge_system_prompt():
    return f"""You are an evaluator. You will be given a task, an AI agent's output, and a single yes/no question about that output.

    Rules:
    - Answer based ONLY on what is present in the output. Do not use outside knowledge.
    - Do not be charitable. If the question is not clearly satisfied, answer NO.
    - Do not reward intent or attempted effort. Reward only concrete evidence in the output.
    - Respond with exactly one word: YES or NO. No explanation, no punctuation, no other text.
"""


def get_scoring_judge_user_prompt(question: str, output: str, initial_task_description: str):
    return f"""Task given to the agent:
    {initial_task_description}

    Agent's output:
    {output}

    Question:
    {question}
"""