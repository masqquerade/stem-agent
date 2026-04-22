from src.llm.workflows.react.react import ReactWorkflow
from src.llm.workflows.plan_then_exec.plan_then_exec import PlanThenExecuteWorkflow
from src.llm.workflows.decompose_and_merge.decompose_and_merge import DecomposeAndMergeWorkflow

WORKFLOWS = {
    "react": ReactWorkflow,
    "plan_then_execute": PlanThenExecuteWorkflow,
    "decompose_and_merge": DecomposeAndMergeWorkflow
}