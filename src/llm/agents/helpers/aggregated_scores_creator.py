def create_aggregated_scores(
        eval_results: list, scoring_function: list
):
    total_tasks = len(eval_results)
    if total_tasks == 0:
        return "no tasks"

    avg = sum(res["scores"].get("overall", 0) for res in eval_results) / total_tasks

    questions_stats = []
    for question in scoring_function:
        q_id = question["id"]
        passes = sum(1 for res in eval_results if res["scores"].get(q_id) == 1)
        pass_rate = (passes / total_tasks) * 100
        questions_stats.append(f"- [{q_id}] {question['question']}: {passes}/{total_tasks} passes ({pass_rate:.0f}%)")

    questions_stats_str = "\n".join(questions_stats)

    return f"""Overall Success Rate: {avg * 100:.1f}%
    
    Question-by-Question Breakdown:
    {questions_stats_str}
"""