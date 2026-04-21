generate_config_schema = {
    "type": "json_schema",
    "name": "config",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "mutation_strategy": {
                "type": "string",
                "enum": [
                    "ADD_TOOL",
                    "REMOVE_TOOL",
                    "DEFAULT",
                    "ADJUST_RESOURCES",
                    "PROMPT_REWRITE"
                ]
            },
            "workflow_type": {
                "type": "string",
                "enum": [
                    "react",
                    "plan_then_execute",
                    "iterative_refinement",
                    "decompose_and_merge"
                ]
            },
            "system_prompt": { "type": "string" },
            "tools": {
                "type": "array",
                "items": { "type": "string" }
            },
            "temperature": { "type": "number" },
            "max_steps": { "type": "integer" },
        },
        "required": [
            "mutation_strategy", "workflow_type",
            "system_prompt", "tools",
            "temperature", "max_steps"
        ],
        "additionalProperties": False
    }
}