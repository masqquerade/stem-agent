generate_plan_pte_schema = {
    "type": "json_schema",
    "name": "plan",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "steps": {
                "type": "array",
                "items": { "type": "string" }
            }
        },
        "required": ["steps"],
        "additionalProperties": False
    }
}