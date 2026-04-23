def get_plan_prompt(task: str):
    return f"""
    CRITICAL ARCHITECTURAL CONSTRAINTS:
    1. Your ONLY job is to plan information-gathering and research steps.
    2. You MUST NOT generate any steps related to drafting, writing, synthesizing, or formatting the final report. 
    3. DO NOT include steps like "Draft a decision matrix", "Write the proposal", or "Synthesize the findings". 
    4. The final synthesis will be handled by a separate system. Your plan must end immediately after the final piece of data is collected via web_search or code_interpreter.
"""