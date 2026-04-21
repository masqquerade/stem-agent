def get_combine_prompt(
        task: str,
        parts: list
):
    return f"Original task: {task}\n\nCompleted steps:\n{parts}\n\nSynthesize a final answer."