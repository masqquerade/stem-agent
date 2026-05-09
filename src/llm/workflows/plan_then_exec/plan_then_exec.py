import json

from src.llm.workflows.base import BaseWorkflow, TraceEvent
import src.llm.logger as logger
from src.llm.workflows.plan_then_exec.prompts.combine_prompt import get_combine_prompt
from src.llm.workflows.plan_then_exec.prompts.get_plan_prompt import get_plan_prompt
from src.llm.workflows.plan_then_exec.schemas.generate_plan_schema import generate_plan_pte_schema
from src.llm.workflows.react.react import ReactWorkflow


class PlanThenExecuteWorkflow(BaseWorkflow):
    def run(self, task: str) -> tuple[str, bool, list[TraceEvent]]:
        self.trace = []

        react_workflow = ReactWorkflow(
            self.llm_client,
            self.config,
            self.schemas,
            self.executors,
            is_subtask=True
        )

        # Generate the plan
        plan_ctx = [
            {"role": "system", "content": self.config.system_prompt},
            {
                "role": "user",
                "content": get_plan_prompt(task)
            }
        ]

        response, _ = self.llm_client.call(
            context=plan_ctx,
            label="[GENERATE][PTE]: plan",
            model=self.model,
            temperature=self.config.temperature,
            response_format=generate_plan_pte_schema
        )

        steps = json.loads(response.output_text)["steps"]
        print(f"  [plan_then_execute] {len(steps)} step(s) planned")
        local_ctx = []
        state = True

        # Execute each part using ReAct
        for step in steps:
            prior_knowledge = ""
            if local_ctx:
                prior_knowledge = "\n\n".join(local_ctx)

            worker_prompt = f"MASTER OBJECTIVE AND DATA PAYLOADS:\n{task}\n\nSUB-TASK TO EXECUTE:\n{step}"

            res_text, state, _ = react_workflow.run(worker_prompt, previous_results=prior_knowledge)
            self.trace.extend(react_workflow.trace)
            local_ctx.append(f"Step: {step}\nResult: {res_text}")
            if not state:
                logger.workflow_result("plan_then_execute", len(self.trace), self.config.max_steps, False)
                break

        # Combine results and return
        system_prompt = self.config.system_prompt
        if self.config.output_format_prompt:
            system_prompt += f"\n\nFINAL OUTPUT FORMATTING RULES:\n{self.config.output_format_prompt}"

        ctx = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": get_combine_prompt(task, local_ctx)
            }
        ]

        combination, _ = self.llm_client.call(
            context=ctx,
            label="[GENERATE][PTE]: combine",
            model=self.model,
            temperature=self.config.temperature
        )

        logger.workflow_result("plan_then_execute", len(self.trace), self.config.max_steps, state)
        return combination.output_text, state, self.trace

