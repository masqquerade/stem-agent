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
            reasoning_effort: str = None
    ):
        kwargs: dict = {
            "model": model,
            "input": context,
        }

        if reasoning_effort:
            kwargs["reasoning"] = { "effort": reasoning_effort }

        if temperature:
            kwargs["temperature"] = temperature

        if tools:
            kwargs["tools"] = tools

        if response_format:
            kwargs["text"] = { "format": response_format }

        start = time.perf_counter()
        response = self.client.responses.create(**kwargs)
        latency_ms = int((time.perf_counter() - start) * 1000)

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

        return response