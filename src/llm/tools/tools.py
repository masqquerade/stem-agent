def read_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()[:50000]

def write_file(path: str, content: str) -> str:
    with open(path, 'w') as f:
        f.write(content)
    return f"Wrote {len(content)} bytes to {path}"

CUSTOM_TOOLS = {
    "read_file": {
        "fn": read_file,
        "schema": {
            "type": "function",
            "name": "read_file",
            "description": "Read a file from disk",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": { "type": "string" }
                },
                "required": ["path"],
                "additionalProperties": False
            },
            "strict": True,
        }
    },

    "write_file": {
        "fn": write_file,
        "schema": {
            "type": "function",
            "name": "write_file",
            "description": "Write to a file from disk",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": { "type": "string" },
                    "content": { "type": "string" }
                },
                "required": ["path", "content"],
                "additionalProperties": False,
            },
            "strict": True
        }
    }
}

BUILTIN_TOOLS = {
    "web_search": {"type": "web_search"},
    "code_interpreter": {"type": "code_interpreter", "container": {"type": "auto"}},
}

def get_tools(tool_names: list[str]) -> tuple[list, dict]:
    schemas = []
    executors = {}

    for name in tool_names:
        if name in BUILTIN_TOOLS:
            schemas.append(BUILTIN_TOOLS[name])

        if name in CUSTOM_TOOLS:
            schemas.append(CUSTOM_TOOLS[name])
            executors[name] = CUSTOM_TOOLS[name]["fn"]

    return schemas, executors