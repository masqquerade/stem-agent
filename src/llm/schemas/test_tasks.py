generated_tasks_schema = {
    "type": "json_schema",
    "name": "test_suite",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "tasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "task_description": {"type": "string"},
                        "diversity_justification": {"type": "string"}
                    },
                    "required": ["task_id", "task_description", "diversity_justification"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["tasks"],
        "additionalProperties": False
    }
}
