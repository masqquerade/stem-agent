import json
import time
from dataclasses import dataclass

from openai import OpenAI

@dataclass
class LLMCallRecord:
    label: str
    model: str
    temperature: float | None
    input_tokens: int
    output_tokens: int
    latency_ms: int
    has_tool_calls: bool
    timestamp: float
    reasoning_effort: str
    # iteration: int | None
    phase: str


def execute_tools(
        response,
        executors: dict
):
    tools_outputs = []

    for item in response.output:
        if item.type == "function_call":
            args = json.loads(item.arguments)
            result = executors[item.name](**args)
            tools_outputs.append({
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": str(result)
            })

    return tools_outputs


class LLMClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.log: list[LLMCallRecord] = []
        self.current_phase = "sense"

    def set_phase(self, phase: str):
        self.current_phase = phase

    def call(
            self,
            context: list[dict],
            label: str,
            model: str ="o3-mini",
            temperature: float = None,
            tools: list[dict] = None,
            response_format: dict = None,
            reasoning_effort: str = None,
    ):
        kwargs: dict = {
            "model": model,
            "input": context,
        }

        if reasoning_effort:
            kwargs["reasoning"] = { "effort": reasoning_effort }

        if temperature is not None:
            kwargs["temperature"] = temperature

        if tools:
            kwargs["tools"] = tools

        if response_format:
            kwargs["text"] = { "format": response_format }

        start = time.perf_counter()
        response = self.client.responses.create(**kwargs)
        latency_ms = int((time.perf_counter() - start) * 1000)
        for item in response.output:
            print(item.type)
        has_tool_calls = any(
            item.type == "function_call" for item in response.output
        )

        record = LLMCallRecord(
                label=label,
                model=model,
                temperature=temperature,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                latency_ms=latency_ms,
                has_tool_calls=has_tool_calls,
                timestamp=time.time(),
                reasoning_effort=reasoning_effort,
                phase=self.current_phase,
        )

        self.log.append(record)

        print(record)

        return response, record

    # Wrapper for agent calls
    def call_agentic(self,
                     context: list[dict],
                     label: str,
                     tools: list[dict] = None,
                     temperature=0.3):
        return self.call(
            context=context,
            label=label,
            model="gpt-4o",
            temperature=temperature,
            tools=tools,
        )