def get_run_baseline_system_prompt(problem_class: str, initial_task_description: str):
    return f"""
    The task scope is: {problem_class}.
    Your task: {initial_task_description}
"""