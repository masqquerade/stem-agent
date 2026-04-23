def get_analyse_exec_trace_prompt(
        task_description: str,
        task_scores: str,
        execution_trace: list
):
    return f"""
    You are a QA Tester analyzing an AI agent's execution trace.

    Task Assigned to Agent:
    {task_description}

    Rubric Scores for this Task:
    {task_scores}

    Execution Trace (Pruned):
    {execution_trace}

    Your job is strictly mechanical. Look at the Rubric Scores. For every question that scored a 0 (Fail), look at the Execution Trace and explain exactly what the agent did or failed to do mechanically that caused the failure. 
    Do not suggest architectural fixes. Do not reflect on prompts. Just report the mechanical chain of events.
    
    Output trict JSON matching the schema.
"""