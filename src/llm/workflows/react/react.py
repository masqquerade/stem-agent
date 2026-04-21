from src.llm.api.llm_client import LLMClient, execute_tools
from src.llm.workflows.base import BaseWorkflow

class ReactWorkflow(BaseWorkflow):
    # result and state (failure or success)
    def run(self, task: str) -> tuple[str, bool]:
        user_input = {
            "role": "user",
            "content": task
        }

        context = [
            {"role": "system", "content": self.config.system_prompt},
            user_input
        ]

        response = None

        for step in range(self.config.max_steps):
            response, record = self.llm_client.call_agentic(
                context=context,
                label=f"[GENERATE][ReAct]: step {step}",
                tools=self.schemas,
                temperature=self.config.temperature
            )

            if not record.has_tool_calls:
                return response.output_text, True

            tool_outputs = execute_tools(
                response, self.executors
            )

            context = context + list(response.output) + tool_outputs

        if response is None:
            return "", False

        # task may be incomplete cause of lack of steps -> False
        return response.output_text, False