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
                    "CHANGE_WORKFLOW",
                    "ADJUST_RESOURCES",
                    "PROMPT_REWRITE",
                    "INITIAL_DESIGN"
                ]
            },
            "mutation_log": { "type": "string" },
            "workflow_type": {
                "type": "string",
                "enum": [
                    "react",
                    "plan_then_execute",
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
            "output_format_prompt": { "type": "string" },
        },
        "required": [
            "mutation_strategy", "workflow_type",
            "system_prompt", "tools",
            "temperature", "max_steps", "mutation_log",
            "output_format_prompt"
        ],
        "additionalProperties": False
    }
}