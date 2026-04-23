ledger_rules_schema = {
    "type": "json_schema",
    "name": "ledger_rules",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "rules": {
                "type": "array",
                "description": "The newly generated Ledger Rules.",
                "items": {"type": "string"}
            }
        },
        "required": ["rules"],
        "additionalProperties": False
    }
}