from dataclasses import dataclass

from src.llm.api.llm_client import LLMClient

# Schemas
from src.llm.schemas.scoring import build_scoring_func_response_schema

# Prompts
from src.llm.prompts.prompts import get_build_scoring_func_system_prompt

@dataclass
class Target:
    problem_class: str
    initial_task_description: str

class StemAgent:
    def __init__(
            self,
            api_key: str,
            target: Target,
            th_model: str = "o3-mini",
            base_model: str = "gpt-4o"
    ):
        self.llm_client = LLMClient(api_key=api_key)
        self.target = target
        self.base_model = base_model
        self.th_model = th_model

    ## should be underscored
    def build_scoring_function(self):
        response = self.llm_client.call(
            context=[{
                "role": "developer",
                "content": get_build_scoring_func_system_prompt(
                self.target.problem_class,
                initial_task_description=self.target.initial_task_description
            )}],
            model=self.th_model,
            label="[SENSE]: Build scoring function",
            response_format=build_scoring_func_response_schema,
            reasoning_effort="high"
        )

        return response


    def run_baseline(self):
        """
        Running baseline is a single LLM call without any agentic features (including tools calling).
        If function calling is required in the specific task, the LLM will only describe a tool it
        would call in a normal situation and assume, that this call succeed. Next, the scoring function
        will score the logged result of the baseline to have a "before" scoring. The more intelligent model
        will get (log, scoring_result) tuple as input to reflex for further improvement.
        """


        pass

    def _sense(self):
        """
        SENSE phase operates with raw input data from the user.
        This stage is divided into several parts:
            1. Generating a scoring function for continuous improving of the target agent.
            2. Running a baseline and scoring it.
            3. Creating several diverse test tasks from the same problems-class to prevent overfitting.
        """

        # 1. Generate a scoring function

        pass