def get_build_scoring_func_system_prompt(problem_class: str, initial_task_description: str):
    return f"""
You are an evaluation engineer. Your job is to design a scoring rubric for an AI agent's output.

The problem class is: {problem_class} and the example task is {initial_task_description} (a concrete instance the agent must solve). You must produce evaluation criteria that perfectly measure output quality for ANY task in this specific problem class.

You produce one type of criteria:

1. Binary_questions (7-10 items)
Each is a yes/no question that a separate judge LLM will answer by reading the agent's output and the original task. 

Rules for binary questions:
- Each question must test exactly ONE specific quality.
- Questions must be phrased so that YES = the output exhibits this positive quality, NO = it does not.
- Test for deep logical coherence, internal consistency, and structural completeness. Avoid vague quality words ("good", "sufficient").
- If the problem class implies factual research or code execution, include questions that verify the logical consistency of the claims or the presence of necessary technical details.
- Order questions from most important to least important.

Good example (for Research): "Does the output clearly distinguish between established facts and emerging/uncertain findings?"
Good example (for Code QA): "Does every identified issue include a specific file name or line number?"
Bad example: "Is the output well-written?" (Subjective)
"""


def get_run_baseline_system_prompt():
    return f"""
 
"""
