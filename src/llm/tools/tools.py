import json

from src.db.db import VectorDatabase


def read_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read()[:50000]


def write_file(path: str, content: str) -> str:
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
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
            "description": "Write content to a file on disk",
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
    },
}

BUILTIN_TOOLS = {
    "web_search": {
        "type": "web_search"
    },
    "code_interpreter": {
        "type": "code_interpreter", "container": {"type": "auto"}
    },
}

SEARCH_KB_SCHEMA = {
    "type": "function",
    "name": "search_knowledge_base",
    "description": "Search the internal knowledge base for relevant information using a natural language query.",
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"],
        "additionalProperties": False,
    },
    "strict": True
}

def make_search_tool(db: VectorDatabase):
    import dataclasses
    def search_knowledge_base(query: str) -> str:
        results = db.query([query], n_results=3)
        serializable = [[dataclasses.asdict(r) for r in batch] for batch in results]
        return json.dumps(serializable, indent=2)
    return search_knowledge_base

def get_tools(tool_names: list[str], db: VectorDatabase = None) -> tuple[list, dict]:
    schemas = []
    executors = {}

    for name in tool_names:
        if name in BUILTIN_TOOLS:
            schemas.append(BUILTIN_TOOLS[name])

        elif name == "search_knowledge_base":
            if db is None:
                raise ValueError("db instance in required")
            schemas.append(SEARCH_KB_SCHEMA)
            executors["search_knowledge_base"] = make_search_tool(db)

        if name in CUSTOM_TOOLS:
            schemas.append(CUSTOM_TOOLS[name]["schema"])
            executors[name] = CUSTOM_TOOLS[name]["fn"]

    return schemas, executors
