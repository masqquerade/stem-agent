import json
from concurrent.futures import ThreadPoolExecutor

from src.llm.workflows.base import BaseWorkflow, TraceEvent
import src.llm.logger as logger
from src.llm.workflows.decompose_and_merge.prompts.decompose_prompt import get_decompose_prompt
from src.llm.workflows.decompose_and_merge.prompts.merge_prompt import get_merge_prompt
from src.llm.workflows.decompose_and_merge.schemas.decompose_schema import decompose_schema
from src.llm.workflows.react.react import ReactWorkflow


class DecomposeAndMergeWorkflow(BaseWorkflow):
    def run(self, task: str) -> tuple[str, bool, list[TraceEvent]]:
        self.trace = []

        react_workflow = ReactWorkflow(
            self.llm_client,
            self.config,
            self.schemas,
            self.executors,
            is_subtask=True
        )

        # Decompose
        decomp_ctx = [
            {"role": "system", "content": self.config.system_prompt},
            {
                "role": "user",
                "content": get_decompose_prompt(task)
            }
        ]

        response, _ = self.llm_client.call(
            context=decomp_ctx,
            label="[GENERATE][DAM]: decompose",
            model=self.model,
            temperature=self.config.temperature,
            response_format=decompose_schema
        )

        subtasks = json.loads(response.output_text)["subtasks"]
        print(f"  [decompose_and_merge] {len(subtasks)} subtask(s) — running in parallel")

        def run_subtask(subtask):
            # Create a fresh workflow instance for each thread
            worker_workflow = ReactWorkflow(
                self.llm_client,
                self.config,
                self.schemas,
                self.executors,
                is_subtask=True
            )

            # Prepend original task to subtask to ensure virtual files/payloads are available
            worker_prompt = f"MASTER OBJECTIVE AND DATA PAYLOADS:\n{task}\n\nSUB-TASK TO EXECUTE:\n{subtask['worker_prompt']}"

            result, state, _ = worker_workflow.run(worker_prompt)
            return {
                "task": subtask["task"],
                "result": result,
                "state": state,
                "trace": list(worker_workflow.trace)
            }

        with ThreadPoolExecutor() as executor:
            worker_results = list(executor.map(run_subtask, subtasks))

        results = []
        any_failed = False
        for res in worker_results:
            self.trace.extend(res["trace"])
            results.append(f"Subtask: {res['task']}\nResult: {res['result']}")
            if not res["state"]:
                any_failed = True

        if any_failed:
            logger.workflow_result("decompose_and_merge", len(self.trace), self.config.max_steps, False)

        system_prompt = self.config.system_prompt
        if self.config.output_format_prompt:
            system_prompt += f"\n\nFINAL OUTPUT FORMATTING RULES:\n{self.config.output_format_prompt}"

        merge_ctx = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": get_merge_prompt(task, results)
            }
        ]

        merged, _ = self.llm_client.call(
            context=merge_ctx,
            label="[GENERATE][DAM]: merge",
            model=self.model,
            temperature=self.config.temperature,
        )

        final_state = not any_failed
        logger.workflow_result("decompose_and_merge", len(self.trace), self.config.max_steps, final_state)
        return merged.output_text, final_state, self.trace