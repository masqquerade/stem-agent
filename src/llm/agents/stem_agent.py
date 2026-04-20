import json
from dataclasses import dataclass

from src.llm.api.llm_client import LLMClient, execute_tools

# Schemas
from src.llm.schemas.scoring import build_scoring_func_response_schema

# Prompts
from src.llm.prompts.prompts import *

# Tools
from src.llm.tools.tools import (
    CUSTOM_TOOLS,
    BUILTIN_TOOLS,
    get_tools
)

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
        self.scoring_function = None

    ## should be underscored
    def build_scoring_function(self):
        response, _ = self.llm_client.call(
            context=[{
                "role": "user",
                "content": get_build_scoring_func_system_prompt(
                    self.target.problem_class,
                    self.target.initial_task_description
                )
            }],
            model=self.th_model,
            label="[SENSE]: Build scoring function",
            response_format=build_scoring_func_response_schema,
            reasoning_effort="high"
        )

        result = json.loads(response.output_text)

        self.scoring_function = result["binary_questions"]
        return self.scoring_function

    def score_output(self, output: str):
        if not self.scoring_function:
            return None

        scores = {}

        for question in self.scoring_function:
            response, _ = self.llm_client.call(
                context=[
                    {
                        "role": "system",
                        "content": get_scoring_judge_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": get_scoring_judge_user_prompt(
                            question,
                            output,
                            self.target.initial_task_description
                        )
                    }
                ],
                model=self.base_model,
                label=f"[SCORING]: Scoring an output for question: {question}",
            )

            answer = response.output_text.strip().upper()
            scores[question["id"]] = 1 if answer.startswith("YES") else 0

        scores["overall"] = sum(scores.values()) / len(self.scoring_function)

        return scores

    def run_baseline(self):
        tools_names = [*CUSTOM_TOOLS, *BUILTIN_TOOLS]
        schemas, executors = get_tools(tools_names)

        user_msg = {
            "role": "user",
            "content": get_run_baseline_system_prompt(
                self.target.problem_class,
                self.target.initial_task_description
            )
        }

        response, record = self.llm_client.call(
            context=[user_msg],
            model=self.base_model,
            label="[SENSE]: Run a baseline",
            tools=schemas,
            temperature=0.3,
        )

        if not record.has_tool_calls:
            return response.output_text

        feedback = execute_tools(
            response,
            executors
        )

        response, _ = self.llm_client.call(
            context=[
                user_msg,
                *response.output,
                *feedback
            ],
            model=self.base_model,
            label="[SENSE]: Run a baseline",
            tools=schemas,
            temperature=0.3,
        )

        return response.output_text

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