_LINE = "─" * 64


def phase(name: str):
    print(f"\n{_LINE}")
    print(f"  {name}")
    print(_LINE)


def scoring_function(questions: list):
    print(f"  Rubric ({len(questions)} questions):")
    for q in questions:
        print(f"    [{q['id']}] {q['question']}")


def score_table(scores: dict, questions: list, label: str = ""):
    header = f"  Scores — {label}" if label else "  Scores"
    print(header)
    for q in questions:
        qid = q["id"]
        val = scores.get(qid, 0)
        mark = "✓" if val == 1 else "✗"
        print(f"    {mark}  [{qid}]  {q['question'][:65]}")
    print(f"         overall: {scores.get('overall', 0):.2f}")


def config_summary(config, iteration: int):
    log = config.mutation_log
    print(f"\n  Config [iter {iteration}]")
    print(f"    workflow   : {config.workflow_type}")
    print(f"    mutation   : {config.mutation_strategy}")
    print(f"    tools      : {config.tools}")
    print(f"    temp/steps : {config.temperature} / {config.max_steps}")
    print(f"    hypothesis : {log[:180]}{'...' if len(log) > 180 else ''}")


def eval_summary(eval_results: list, questions: list):
    n = len(eval_results)
    print(f"\n  Evaluation ({n} tasks):")

    for res in eval_results:
        overall = res["scores"].get("overall", 0)
        steps = len(res["trace"])

        tool_counts: dict = {}
        for event in res["trace"]:
            for te in event.get("tool_executions", []):
                name = te.get("name", "")
                if name in ("message", "reasoning"):
                    continue
                tool_counts[name] = tool_counts.get(name, 0) + 1

        tools_str = "  ".join(f"{k}×{v}" for k, v in tool_counts.items()) or "no tools"
        state = "PASS" if overall >= 1.0 else ("FAIL" if overall == 0.0 else f"{overall:.2f}")
        print(f"    [{res['task_id']}]  {state:<6}  {steps} steps  {tools_str}")

    total = max(n, 1)
    print(f"\n  Per-question pass rates:")
    for q in questions:
        qid = q["id"]
        passes = sum(1 for r in eval_results if r["scores"].get(qid) == 1)
        bar = "█" * passes + "░" * (total - passes)
        print(f"    [{qid}]  {bar}  {passes}/{total}")

    avg = sum(r["scores"].get("overall", 0) for r in eval_results) / total
    print(f"\n    avg: {avg:.2f}")


def ledger_update(new_rules: list, all_rules: list):
    if not new_rules:
        print("  No new ledger rules (perfect run).")
        return
    print(f"\n  New rules ({len(new_rules)}):")
    for rule in new_rules:
        print(f"    → {rule[:120]}{'...' if len(rule) > 120 else ''}")
    print(f"\n  Ledger total: {len(all_rules)} rule(s)")


def workflow_result(workflow_type: str, steps_taken: int, max_steps: int, success: bool):
    if success:
        print(f"  [{workflow_type}] done — {steps_taken} step(s)")
    else:
        print(f"  [{workflow_type}] INCOMPLETE — hit {max_steps}-step limit after {steps_taken} step(s)")


def tool_call(name: str, args: dict):
    key_arg = ""
    if args:
        first_val = str(next(iter(args.values()), ""))
        key_arg = f"  {first_val[:70]}"
    print(f"    → {name}{key_arg}")


def tool_error(name: str, error_msg: str):
    print(f"    ✗ {name} FAILED: {error_msg}")


def error(context: str, msg: str):
    print(f"  [ERR] {context}: {msg}")


def run_summary(baseline_score: float, config_archive: list):
    print(f"\n{_LINE}")
    print("  Run Summary")
    print(_LINE)
    print(f"  baseline : {baseline_score:.2f}")
    for i, cfg in enumerate(config_archive):
        s = getattr(cfg, "score", 0.0)
        prev = baseline_score if i == 0 else getattr(config_archive[i - 1], "score", 0.0)
        delta = s - prev
        sign = "+" if delta >= 0 else ""
        print(f"  iter {i}   : {s:.2f}  ({sign}{delta:.2f})  [{cfg.workflow_type} / {cfg.mutation_strategy}]")
    print(_LINE)