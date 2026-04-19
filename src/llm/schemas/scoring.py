build_scoring_func_response_schema = {
    "type": "json_schema",
    "name": "scoring_criteria",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "binary_questions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "question": {"type": "string"}
                    },
                    "required": ["id", "question"],
                    "additionalProperties": False
                }
            },
        },
        "required": ["binary_questions"],
        "additionalProperties": False
    }
}
