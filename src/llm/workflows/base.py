from abc import ABC, abstractmethod

from src.llm.api.llm_client import LLMClient
from src.llm.config.agent_config import AgentConfig


class BaseWorkflow(ABC):
    def __init__(self,
            llm_client: LLMClient,
            config: AgentConfig,
            schemas: list,
            executors: dict,
            model: str = "gpt-4o"):
        self.llm_client = llm_client
        self.config = config
        self.schemas = schemas
        self.executors = executors
        self.model = model

    @abstractmethod
    def run(self, task: str) -> tuple[str, bool]:
        pass