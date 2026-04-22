import json

from src.llm.api.llm_client import execute_tools
from src.llm.compression.tool_calling_compressor import compress_tool_output
from src.llm.tools.tools import BUILTIN_TOOLS
from src.llm.workflows.base import BaseWorkflow, TraceEvent, ToolExecution

class ReactWorkflow(BaseWorkflow):
    # result and state (failure or success)
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
            print(f"\n[ReAct step {step}] context ({len(context)} messages):")
            for msg in context:
                role = msg.get("role") if isinstance(msg, dict) else msg.type
                content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
                content_str = str(content)
                print(f"  [{role}]: {content_str[:200]!r}")

            response, record = self.llm_client.call_agentic(
                context=context,
                label=f"[GENERATE][ReAct]: step {step}",
                tools=self.schemas,
                temperature=self.config.temperature
            )

            print(f"\n[ReAct step {step}] response ({len(response.output)} items):")
            for item in response.output:
                if item.type == "message":
                    text = item.content[0].text if item.content else ""
                    print(f"  [message]: {text[:300]!r}")
                elif item.type == "function_call":
                    print(f"  [function_call]: {item.name}({item.arguments[:200]!r})")
                else:
                    print(f"  [{item.type}]")

            if not record.has_tool_calls:
                self._record_step(step, response, [])
                return response.output_text, True, self.trace

            tool_outputs = execute_tools(
                response, self.executors
            )

            print(f"\n[ReAct step {step}] tool outputs:")
            for o in tool_outputs:
                print(f"  [{o.get('call_id', '?')}]: {str(o.get('output', ''))[:200]!r}")

            self._record_step(step, response, tool_outputs)

            context = context + list(response.output) + tool_outputs

        if response is None:
            return "ERROR WHILE REACTING", False, self.trace

        # task may be incomplete cause of lack of steps -> False
        return response.output_text, False, self.trace

    def _record_step(self, step: int, response, tool_outputs: list) -> None:
        thought = next(
            (item.content[0].text for item in response.output if item.type == "message"),
            ""
        )
        executions = []
        for item in response.output:
            if item.type == "function_call" or item.type in BUILTIN_TOOLS:
                output = next(
                    (tool_output["output"] for tool_output in tool_outputs if tool_output["call_id"] == item.call_id),
                    ""
                )
                executions.append(ToolExecution(
                    name=item.name,
                    args=json.loads(item.arguments),
                    is_error=output.startswith("Error"),
                    output_summary=compress_tool_output(
                        tool_name=item.name,
                        raw_output=output
                    )
                ))

        self.trace.append(TraceEvent(step=step, thought=thought, tool_executions=executions))
