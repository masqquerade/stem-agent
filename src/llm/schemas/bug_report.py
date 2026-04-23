bug_report_schema = {
    "type": "json_schema",
    "json_schema": {  # FIXED: Required nesting
        "name": "bug_report",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "report": {
                    "type": "array",
                    "description": "List of failed questions and their specific mechanical failure explanations.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "question_id": {
                                "type": "string",
                                "description": "The ID of the question (e.g., 'Q1', 'Q4')"
                            },
                            "failure_reason": {
                                "type": "string",
                                "description": "The specific mechanical failure explanation."
                            }
                        },
                        "required":["question_id", "failure_reason"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["report"],
            "additionalProperties": False
        }
    }
}