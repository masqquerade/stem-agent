import json

from src.llm.api.llm_client import execute_tools
from src.llm.compression.tool_calling_compressor import compress_tool_output
from src.llm.workflows.base import BaseWorkflow, TraceEvent, ToolExecution
from src.llm.workflows.helpers.sanitizer import sanitize_payload


class ReactWorkflow(BaseWorkflow):
    def run(self, task: str, previous_results: str = "") -> tuple[str, bool, list[TraceEvent]]:
        self.trace = []

        content = task
        if previous_results:
            content = f"Previously completed steps:\n{previous_results}\n\nCurrent step to execute:\n{task}"

        user_input = {
            "role": "user",
            "content": content
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

            executions = []
            for item in response.output:
                if item.type.endswith("_call") and item.type != "function_call":
                    args = sanitize_payload(item)

                    summary_text = "[NATIVE LLM CALL]"

                    if item.type == "web_search_call":
                        action = args.get("action", {})
                        if action is not None:
                            summary_text = f"[web_search_tool] Action: {action.get('type', 'unknown')} - Queries: {action.get('search_queries', [])}"

                    executions.append(ToolExecution(
                        name=item.type,
                        args=args,
                        is_error=False,
                        output_summary=summary_text
                    ))

            if not record.has_tool_calls:
                self._record_step(step, response, executions)
                return response.output_text, True, self.trace

            tool_outputs = execute_tools(
                response, self.executors
            )

            api_tool_outputs = []

            for item in response.output:
                if item.type == "function_call":
                    call_id = getattr(item, "call_id", "")

                    out_dict = next((out for out in tool_outputs if out.get("call_id") == call_id), {})
                    output_str = str(out_dict.get("content", "No output."))

                    args_str = getattr(item, "arguments", "{}")
                    args = json.loads(args_str)

                    executions.append(ToolExecution(
                        name=item.name,
                        args=args,
                        is_error=output_str.startswith("Error"),
                        output_summary=compress_tool_output(
                            tool_name=item.name,
                            raw_output=output_str
                        )
                    ))

                    api_tool_outputs.append({
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": output_str
                    })

            self._record_step(step, response, executions)

            context = context + list(response.output) + api_tool_outputs

        if response is None:
            return "ERROR WHILE REACTING", False, self.trace

        # task may be incomplete cause of lack of steps -> False
        return getattr(response, "output_text", "Error"), False, self.trace

    def _record_step(self, step: int, response, executions: list[ToolExecution]):
        thought = ""
        for item in response.output:
            if item.type == "message":
                text_blocks = [block.text for block in getattr(item, "content", []) if getattr(block, "type", "") == "output_text"]
                if text_blocks:
                    thought = "".join(text_blocks)
                    break

        self.trace.append(TraceEvent(step=step, thought=thought, tool_executions=executions))
