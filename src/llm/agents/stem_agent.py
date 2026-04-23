import dataclasses
import json
from dataclasses import dataclass

from src.llm.agents.helpers.aggregated_scores_creator import create_aggregated_scores
from src.llm.api.llm_client import LLMClient, execute_tools
from src.llm.config.agent_config import AgentConfig
from src.llm.prompts.analyse_exec_trace_prompt import get_analyse_exec_trace_prompt
from src.llm.prompts.create_test_tasks_prompt import create_test_task_prompt
from src.llm.prompts.generate_config_prompt import generate_config_init_prompt, generate_config_prompt
from src.llm.prompts.reflect_prompt import get_reflect_prompt
from src.llm.schemas.bug_report import bug_report_schema
from src.llm.schemas.config import generate_config_schema
from src.llm.schemas.ledger_rules import ledger_rules_schema

# Schemas
from src.llm.schemas.scoring import build_scoring_func_response_schema

# Prompts
from src.llm.prompts.build_scoring_func_prompt import get_build_scoring_func_system_prompt
from src.llm.prompts.run_baseline_prompt import get_run_baseline_system_prompt
from src.llm.prompts.scoring_judge_prompt import get_scoring_judge_system_prompt, get_scoring_judge_user_prompt
from src.llm.schemas.test_tasks import generated_tasks_schema

# Tools
from src.llm.tools.tools import (
    CUSTOM_TOOLS,
    BUILTIN_TOOLS,
    get_tools
)
from src.llm.workflows.registry import WORKFLOWS


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
        self.baseline_scoring = None
        self.config_archive: list[AgentConfig] = []
        self.test_sample = []
        self.current_config: AgentConfig | None = None
        self.ledger: list[str] = []

    # Preparation
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
            label="[PREPARATION]: Build scoring function",
            response_format=build_scoring_func_response_schema,
            reasoning_effort="high"
        )

        result = json.loads(response.output_text)

        self.scoring_function = result["binary_questions"]
        return self.scoring_function

    def _build_test_sample(self):
        prompt = create_test_task_prompt(
            task=self.target.initial_task_description,
            problem_class=self.target.problem_class
        )

        ctx = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        response, _ = self.llm_client.call(
            context=ctx,
            label="[PREPARATION]: build test sample",
            model=self.th_model,
            response_format=generated_tasks_schema,
            reasoning_effort="high"
        )

        tasks_dict = json.loads(response.output_text)
        self.test_sample = tasks_dict["tasks"]

    def score_output(self, output: str, task_description: str = None):
        if not self.scoring_function:
            return None

        task_description = task_description or self.target.initial_task_description

        scores = {}

        for question in self.scoring_function:
            user_prompt = get_scoring_judge_user_prompt(
                question["question"],
                output,
                task_description
            )

            response, _ = self.llm_client.call(
                context=[
                    {
                        "role": "system",
                        "content": get_scoring_judge_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model=self.base_model,
                label=f"[SCORING]: {question['id']}",
            )

            answer = response.output_text.strip().upper()
            scores[question["id"]] = 1 if answer.startswith("YES") else 0

        scores["overall"] = sum(scores.values()) / len(self.scoring_function)

        return scores

    def run_baseline(self):
        tools_names = []
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
            label="[PREPARATION]: Run a baseline",
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
            label="[PREPARATION]: Run a baseline",
            tools=schemas,
            temperature=0.3,
        )

        return response.output_text

    def _prepare(self):
        self.build_scoring_function()
        self._build_test_sample()

        baseline_output = self.run_baseline()

        scoring = self.score_output(baseline_output)
        self.baseline_scoring = scoring

    # Generation (set self.current_config)
    def _generate(self, iteration: int) -> AgentConfig:
        if iteration == 0:
            return self._generate_initial()

        parent = max(self.config_archive, key=lambda x: x.score)
        return self._generate_mutation(parent)

    def _generate_initial(self) -> AgentConfig:
        tools_names = [*CUSTOM_TOOLS, *BUILTIN_TOOLS]

        prompt = generate_config_init_prompt(
            problem_class=self.target.problem_class,
            baseline_score=self.baseline_scoring["overall"],
            scores=self.baseline_scoring,
            scoring_function=self.scoring_function,
            tool_list=tools_names
        )

        ctx = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        response, _ = self.llm_client.call(
            context=ctx,
            label="[GENERATE][INIT]: generate initial config",
            model=self.th_model,
            response_format=generate_config_schema,
            reasoning_effort="high"
        )

        config_dict = json.loads(response.output_text)
        config = AgentConfig.from_dict(config_dict)

        return config

    def _generate_mutation(self, parent: AgentConfig) -> AgentConfig:
        tools_names = [*CUSTOM_TOOLS, *BUILTIN_TOOLS]

        prompt = generate_config_prompt(
            problem_class=self.target.problem_class,
            scoring_function=self.scoring_function,
            parent_config=parent,
            scores=parent.scoring,
            tool_list=tools_names,
            ledger=json.dumps(self.ledger, indent=2)
        )

        ctx = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        response, _ = self.llm_client.call(
            context=ctx,
            label="[GENERATE][INIT]: generate mutation config",
            model=self.th_model,
            response_format=generate_config_schema,
            reasoning_effort="high"
        )

        config_dict = json.loads(response.output_text)
        config = AgentConfig.from_dict(config_dict)

        return config

    def _evaluate(self):
        schemas, executors = get_tools(self.current_config.tools)

        agent_workflow = WORKFLOWS[self.current_config.workflow_type](
            llm_client=self.llm_client,
            config=self.current_config,
            schemas=schemas,
            executors=executors,
        )

        evaluation_results = []

        # should be parallel
        for task in self.test_sample:
            result, state, trace = agent_workflow.run(task["task_description"])

            scores = self.score_output(result, task["task_description"])

            result = {
                "task_id": task["task_id"],
                "task_description": task["task_description"],
                "success_state": state,
                "trace": [dataclasses.asdict(event) for event in trace], # for map stage
                "scores": scores,
                "bug_report": []
            }

            evaluation_results.append(result)

        return evaluation_results

    def reflect(self, eval_results: list):
        failed_results = []

        for result in eval_results:
            scores = result["scores"]

            if any(score == 0 for key, score in scores.items() if key != "overall"):
                failed_results.append(result)

        if not failed_results:
            print("[REFLECT]: perfect run. no rules generated")
            return []

        for result in failed_results:
            # generate bug report (map)
            ctx = [
                {
                    "role": "user",
                    "content": get_analyse_exec_trace_prompt(
                        task_description=result["task_description"],
                        task_scores=result["scores"],
                        execution_trace=result["trace"]
                    )
                }
            ]

            response, _ = self.llm_client.call(
                context=ctx,
                label=f"[REFLECT][MAP]: generate bug report for {result['task_id']}",
                model=self.base_model,
                response_format=bug_report_schema
            )

            output_text = getattr(response, "output_text", "{}")

            try:
                parsed_response = json.loads(output_text)
                bug_report = parsed_response.get("report", [])
            except json.JSONDecodeError:
                print(f"[ERROR] Failed to parse bug report for {result['task_id']}")
                bug_report = []

            result["bug_report"] = bug_report

        # create ledger rules (reduce)
        bugs_summary = []

        for result in failed_results:
            for bug in result["bug_report"]:
                bugs_summary.append({
                    "task_id": result["task_id"],
                    "question_id": bug["question_id"],
                    "failure_reason": bug["failure_reason"]
                })

        ctx = [
            {
                "role": "user",
                "content": get_reflect_prompt(
                    current_config=self.current_config,
                    aggregated_score_text=create_aggregated_scores(
                        eval_results=eval_results,
                        scoring_function=self.scoring_function
                    ),
                    map_summaries=json.dumps(bugs_summary, indent=2)
                )
            }
        ]

        response, _ = self.llm_client.call(
            context=ctx,
            label="[REFLECT][REDUCE]: create ledger rules",
            model=self.th_model,
            reasoning_effort="high",
            response_format=ledger_rules_schema
        )

        output_text = getattr(response, "output_text", "{}")

        try:
            parsed_response = json.loads(output_text)
            ledger_rules = parsed_response.get("rules", [])
        except json.JSONDecodeError:
            print("[ERROR] Failed to parse ledger rules from LLM response.")
            ledger_rules = []

        # debugggg
        print(f"\n[REFLECT] Generated {len(ledger_rules)} new rules for the Ledger of Truth:")
        for i, rule in enumerate(ledger_rules, 1):
            print(f"  {i}. {rule}")
        #

        return ledger_rules

# добавил бы обработку ошибок в воркфлоу. откат, елси что то пошло
# не так и рефлексия --- еще попытка
# add parallel for decompose and merge
# tell about compression in reflection layer to not exceed the context
# tell more about scoring function (why its an oracle)