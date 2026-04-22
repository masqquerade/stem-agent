def create_test_task_prompt(task: str, problem_class: str, tasks_count: int = 2):
    return f"""
    You are an elite Benchmark Engineer. Your objective is to create a robust, generalized test suite for an AI agent operating in the following problem class: {problem_class}.

    The user has submitted an original task: 
    {task}

    You must generate exactly {tasks_count} test tasks. 
    Rules for the test suite:
    1. HOLD OUT THE ORIGINAL: Do not include the user's original task. The agent will only see that at the very end of its evolution.
    2. FORCE DIVERSITY: The 5 tasks must test different edges of the problem class. Vary the length, the required depth, the tone, and the constraints. 
    3. REALISM: The tasks must look like real user prompts, not robotic instructions.

    Output a JSON array of {tasks_count} tasks. For each task, provide a `task_description` (the prompt the agent will receive) and a `diversity_justification` (a 1-sentence explanation of what specific capability this task tests compared to the others).   
"""