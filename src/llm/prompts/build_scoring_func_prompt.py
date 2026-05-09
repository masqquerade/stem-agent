def get_build_scoring_func_system_prompt(problem_class: str, initial_task_description: str):
    return f"""You are an evaluation engineer. Design a scoring rubric that measures output quality for a specific problem domain.

Problem class: {problem_class}
Example task (for context): {initial_task_description}

Produce 5-8 binary yes/no questions that a judge LLM will answer by reading the agent's output.

PRINCIPLE: Measure what makes output truly EXCELLENT for this specific domain. Do not be charitable. An excellent output should be indistinguishable from a senior expert's report. 

CALIBRATION GOAL: Design questions that are difficult to satisfy with a simple zero-shot LLM call. If a naive LLM can answer the question using its internal training data without tools, the question is likely TOO EASY. Focus on markers that require active research, precise data, and rigorous cross-referencing.

For this domain, identify the qualities that separate an expert output from a mediocre one:
- Does it find 'hard' data (exact numbers, recent benchmarks, specific citations) that a generic model would lack?
- Does it acknowledge technical nuances that only a specialist would know?
- Does it explicitly verify claims through multiple tool steps?
- Does it explicitly avoid common novice fallacies or generalized assumptions in this domain? (Include at least one question testing for the ABSENCE of a bad practice).

Design questions that test for these excellence markers. They may include:
- Specific, concrete content (exact names, numbers, identifiers, references) vs. generic statements
- Acknowledgment of nuance, edge cases, or limitations where relevant
- Evidence of reasoning or justification for claims made
- Coverage of important aspects a shallow answer would miss
- Correctness markers visible in the output (internal consistency, proper use of domain terminology)

CRITICAL — DOMAIN SPECIFICITY REQUIREMENT:
Your questions MUST be tailored to the specific sub-domain of the example task. For example, if the task is about GPU inference benchmarking, your questions should explicitly ask if the output provides concrete numbers for throughput and latency, rather than a generic "Does the output include concrete details?". 
While you should not hardcode the exact entities from the example task (e.g. don't ask "Does it compare vLLM to TGI"), you MUST ask domain-specific questions (e.g. "Does it explicitly compare the performance of the requested frameworks using standard metrics?").

Rules:
- Each question tests exactly ONE quality
- YES = output has this quality, NO = it does not
- Questions must be answerable from the output alone (no external fact-checking by the judge)
- Questions must apply to tasks within this specific sub-domain
- Order from most important to least important
- Avoid vague quality words ("good", "sufficient", "well-written")
"""