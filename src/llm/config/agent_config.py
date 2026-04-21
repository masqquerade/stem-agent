from dataclasses import dataclass

@dataclass
class AgentConfig:
    mutation_strategy: str
    workflow_type: str
    system_prompt: str
    tools: list[str]
    temperature: float
    max_steps: int

    @classmethod
    def from_dict(cls, d: dict) -> "AgentConfig":
        return cls(**d)