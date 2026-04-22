from src.llm.config.agent_config import AgentConfig


def _format_score_lines(scores: dict, scoring_function: list, failed_only: bool = False) -> str:
    id_to_question = {q["id"]: q["question"] for q in scoring_function}
    lines = [
        f"[{question_id}] {id_to_question[question_id]}: {score}"
        for question_id, score in scores.items()
        if question_id != "overall" and (not failed_only or score == 0)
    ]
    return "\n".join(lines)

def generate_config_init_prompt(
        problem_class: str,
        baseline_score: float,
        scores: dict,
        scoring_function: list,
        tool_list: list
):
    failed_questions_str = _format_score_lines(scores, scoring_function, failed_only=True)

    return f"""
    You are an elite AI System Architect. Your job is to design a specialized AI agent to solve tasks within the following problem class: {problem_class}

    We ran a naive baseline LLM (with tools but no advanced workflow) against this class. It scored {baseline_score}.
    Here are the specific evaluation metrics it failed. These represent capability gaps your new architecture must fix:
    {failed_questions_str}

    You must output a complete, strict JSON configuration for a new agent designed specifically to address these failures.

    ## System Architecture Constraints
    1. `mutation_strategy`: You MUST set this exactly to "INITIAL_DESIGN".
    2. `workflow_type`: Select the execution topology (`react`, `plan_then_execute`, `decompose_and_merge`). The Python engine automatically handles the step-by-step routing.
    3. `system_prompt`: MUST NOT contain step-by-step workflow instructions. Instead, write strict identity rules, formatting constraints, and domain-specific knowledge. CRITICAL: the system_prompt must generalize to ANY task within the problem class, not the specific example task used in evaluation. If the tools list includes search or retrieval tools, the system_prompt MUST instruct the agent to use them to gather evidence rather than relying on internal knowledge.
    4. `tools`: Select strictly from the available registry: {tool_list}.
    5. `mutation_log`: Explicitly explain how your chosen workflow, tools, and system prompt resolve the specific baseline failures.
"""

def generate_config_prompt(
        problem_class: str,
        parent_config: AgentConfig,
        scores: dict,
        scoring_function: list,
        tool_list: list,
        ledger: str,  # not implemented yet
):
    per_question_scores_str = _format_score_lines(scores, scoring_function)

    return f"""
    You are an elite AI System Architect evolving a specialized AI agent for the problem class: {problem_class}.

    Here is the current best-performing agent configuration (The Parent):
    {parent_config}

    Here is how the Parent scored on the strict evaluation rubric:
    {per_question_scores_str}

    Here is the "Ledger of Truth"—architectural rules discovered from previous iterations. You MUST NOT repeat failed experiments listed here, and you should leverage proven successes:
    {ledger}

    Your task is to evolve the Parent configuration to fix the remaining failed scores.

    ## Evolving the Architecture
    1. `mutation_strategy`: You MUST select exactly one strategy from ["ADD_TOOL", "REMOVE_TOOL", "CHANGE_WORKFLOW", "ADJUST_RESOURCES", "PROMPT_REWRITE"].
    2. Apply the mutation. If you change the workflow or add a tool, you MUST update the `system_prompt` so it synergizes with your new architecture.

    ## System Architecture Constraints
    1. `workflow_type`: The Python engine handles the step-by-step routing (`react`, `plan_then_execute`, `decompose_and_merge`).
    2. `system_prompt`: MUST NOT contain step-by-step workflow instructions. It must only contain identity rules, formatting constraints, and domain heuristics. CRITICAL: the system_prompt must generalize to ANY task within the problem class, not the specific example task used in evaluation. If the tools list includes search or retrieval tools, the system_prompt MUST instruct the agent to use them to gather evidence rather than relying on internal knowledge.
    3. `tools`: Select strictly from the available registry: {tool_list}.
    4. `mutation_log`: You must justify your chosen `mutation_strategy` and state exactly which failing score you expect it to improve based on the Ledger.
"""