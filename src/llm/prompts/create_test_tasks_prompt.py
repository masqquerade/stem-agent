def create_test_task_prompt(task: str, problem_class: str, tasks_count: int = 5):
    return f"""
    You are an elite Benchmark Engineer. Your objective is to create a robust, generalized test suite for an AI agent operating in the following problem class: {problem_class}.

    The user has submitted an original task: 
    {task}

    You must generate exactly {tasks_count} test tasks. 
    Rules for the test suite:
    1. HOLD OUT THE ORIGINAL: Do not include the user's original task. The agent will only see that at the very end of its evolution.
    2. FORCE DIVERSITY BUT MAINTAIN DOMAIN: The {tasks_count} tasks must test different edges of the problem class. Vary the length, the required depth, the tone, and the constraints. HOWEVER, they MUST remain strictly within the exact same specific sub-domain or subject matter as the original task. Do not drift to completely different topics within the problem class (e.g., if the task is about NLP frameworks, do not create tasks about distributed databases).
    3. REALISM: The tasks must look like real user prompts, not robotic instructions.
    
    ENVIRONMENTAL CONSTRAINT: This environment is a sandbox. Tasks must be fully self-contained.
    You MUST NOT generate tasks that require reading real files from the local filesystem.
    Instead, embed all necessary file content directly in the task description using labeled Markdown code blocks (e.g., 'File: app.py').

    STRUCTURAL MIRRORING: If the original task involves reading multiple files with import relationships (e.g., code review, codebase audit), your test tasks MUST also embed multi-file virtual codebases where files reference each other. Do not flatten everything into a single file — preserve the cross-file structure so the agent must reason across multiple provided files.

    DATA SOURCE MIRRORING: If the original task requires the agent to search for external information (e.g., threat intelligence, current events, market data, recent advisories), your test tasks MUST also require external data gathering. Do NOT embed all the answers inline — write tasks that require the agent to actively research and retrieve information using web search. A test task that provides all answers in the prompt cannot test whether the agent can gather and verify external data.

    Output a JSON array of {tasks_count} tasks. For each task, provide a `task_description` (the prompt the agent will receive) and a `diversity_justification` (a 1-sentence explanation of what specific capability this task tests compared to the others).   
"""