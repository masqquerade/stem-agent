decompose_schema = {
    "type": "json_schema",
    "name": "plan",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "subtasks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "task": { "type": "string" },
                        "worker_prompt": { "type": "string" }
                    },
                    "required": ["task", "worker_prompt"],
                    "additionalProperties": False
                }
            },
        },
        "required": ["subtasks"],
        "additionalProperties": False
    }
}