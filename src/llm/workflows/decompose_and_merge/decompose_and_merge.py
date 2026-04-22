import json

from src.llm.workflows.base import BaseWorkflow, TraceEvent
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
            self.executors
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

        results = []

        for subtask in subtasks:
            result, state, _ = react_workflow.run(subtask["worker_prompt"])
            self.trace.extend(react_workflow.trace)
            if not state:
                return result, False, self.trace
            results.append(f"Subtask: {subtask['task']}\nResult: {result}")

        merge_ctx = [
            {"role": "system", "content": self.config.system_prompt},
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

        return merged.output_text, True, self.trace