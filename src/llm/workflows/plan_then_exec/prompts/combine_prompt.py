def get_combine_prompt(
        task: str,
        parts: list
):
    return f"""
    Your objective is to review the chronological execution log of a planned workflow and generate a flawless, comprehensive final answer to the user's original task.

    You will receive the <original_task> and the <execution_log> (the sequential outputs of the completed steps).

    You must adhere strictly to the following synthesis rules:

    ## 1. Direct Alignment (The Prime Directive)
    - Your entire focus is answering the <original_task>. 
    - Do not summarize the steps just for the sake of summarizing them. Extract only the information that directly resolves the user's request.
    - If the user requested a specific output format (e.g., a table, a JSON object, a specific tone), you MUST strictly enforce that format in your final output.

    ## 2. Narrative Cohesion (No Meta-Commentary)
    - DO NOT expose the "machine" to the user.
    - Never use phrases like "In Step 1, we found...", "The execution log shows...", or "Based on the completed steps...".
    - Weave the extracted facts into a single, authoritative response as if you researched it yourself in one fluid motion.

    ## 3. Graceful Error Handling
    - In sequential execution, intermediate steps sometimes fail, return errors, or hit dead ends.
    - If the <execution_log> contains errors or missing data, DO NOT copy the errors into the final response. 
    - Synthesize the valithered information you DO have. If the task cannot be fully answered due to a critical step failure, provide the partial answer clearly and state exactly what data could not be retrieved in a professional, user-facing manner.

    ## 4. Deduplication
    - Because steps build on each other, later steps often repeat context from earlier steps. Ruthlessly deduplicate the information so the final answer is dense and punchy.
    
    Original task: {task}
    Execution workflow: {'\n\n'.join(parts)}
"""