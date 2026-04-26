# STEM Agent

An automatic agent architecture search system. Given a problem class and an initial task, STEM evolves a specialized agent configuration (workflow, tools, system prompt) through iterative self-evaluation and reflection.

## Requirements

- OpenAI API key with access to `o3-mini` and `gpt-4o`

## Setup

```bash
git clone https://github.com/masqquerade/stem-agent.git
cd jb_stem
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
API_KEY=sk-...
```

## Running

```bash
python -m src.main
```

You will be prompted for two inputs:

```
=== STEM Agent ===
Problem class: Deep Research
Initial task: Compare latency, cost, and accuracy of hybrid RAG vs. LoRA-tuned Llama-3...
```

The system will then:
1. Build a scoring function and test sample for the problem class
2. Run a zero-shot baseline and score it
3. Run up to 3 evolution iterations (generate config → evaluate → reflect)
4. Execute the original task with the best discovered config and print the result

After the initial task completes, you can submit additional tasks in the same problem class. The evolution loop does not re-run — the already-discovered config is reused. Each task is executed independently with no memory of previous tasks, so each prompt must be self-contained:

```
---
Next task (or 'exit'): Compare SPLADE vs BM25 retrieval on biomedical corpora; include recall@10 benchmarks and a cost estimate for 1M queries.
```

Type `exit` to quit.

## Project structure

```
src/
  main.py                          # CLI entry point
  llm/
    agents/
      stem_agent.py                # Core STEM loop (prepare → generate → evaluate → reflect)
    workflows/
      react/                       # ReAct workflow
      plan_then_exec/              # Plan-then-Execute workflow
      decompose_and_merge/         # Decompose-and-Merge (parallel workers) workflow
    tools/
      tools.py                     # Tool registry (web_search, code_interpreter, read_file, write_file)
    prompts/                       # All LLM prompts
    config/
      agent_config.py              # AgentConfig dataclass
```

## Available tools for generated agents

| Tool | Type | Description |
|---|---|---|
| `web_search` | built-in | Live web search |
| `code_interpreter` | built-in | Execute Python code in a sandbox |
| `read_file` | custom | Read a file from disk |
| `write_file` | custom | Write a file to disk |

The architect LLM selects which tools to give the target agent based on the problem class.
