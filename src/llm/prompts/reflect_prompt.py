from src.llm.config.agent_config import AgentConfig


def get_reflect_prompt(
        current_config: AgentConfig,
        aggregated_score_text: str,
        map_summaries: str
):
    return f"""
    You are an elite AI System Architect. You are evaluating the results of an architectural experiment to build a "Ledger of Truth"—a set of immutable rules for future agent designs.

    ## 1. The Hypothesis
    In the previous generation phase, you created this configuration:
    {current_config}

    Here was your hypothesis for this design:
    {current_config.mutation_log}

    ## 2. The Empirical Reality
    We ran this configuration against 5 diverse test tasks. Here are the aggregated results:
    {aggregated_score_text}

    Here are the mechanical bug reports for how the agent failed on specific tasks:
    {map_summaries}

    ## Your Task
    Compare the Hypothesis against the Empirical Reality. 
    1. Did the hypothesis succeed? (e.g., Did the workflow fix what it was supposed to fix?)
    2. What are the systemic failures? (Ignore isolated anomalies; focus on things that failed across multiple tasks).
    3. Generate 1 to 3 "Ledger Rules".

    A Ledger Rule MUST be:
    - Causal: "Because we used workflow X, problem Y occurred..."
    - Actionable: "...therefore, future mutations must use tool Z or prompt constraint W."
    - Specific: Never write vague rules like "improve reasoning." 

    Output a strict JSON array of these string rules.   
"""