from dataclasses import dataclass

@dataclass
class AgentConfig:
    mutation_strategy: str
    workflow_type: str
    system_prompt: str
    tools: list[str]
    temperature: float
    max_steps: int
    score: float
    scoring: dict
    mutation_log: str
    output_format_prompt: str

    @classmethod
    def from_dict(cls, d: dict) -> "AgentConfig":
        return cls(
            mutation_strategy=d["mutation_strategy"],
            workflow_type=d["workflow_type"],
            system_prompt=d["system_prompt"],
            tools=d["tools"],
            temperature=d["temperature"],
            max_steps=d["max_steps"],
            mutation_log=d["mutation_log"],
            output_format_prompt=d.get("output_format_prompt", ""),
            score=d.get("score", 0.0),
            scoring=d.get("scoring", {}),
        )