import json

def sanitize_payload(obj):
    if hasattr(obj, "model_dump_json"):
        return json.loads(obj.model_dump_json(exclude_none=True))

    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj

    if isinstance(obj, list):
        return [sanitize_payload(item) for item in obj]
    if isinstance(obj, dict):
        return {k: sanitize_payload(v) for k, v in obj.items() if not str(k).startswith('_')}

    if hasattr(obj, '__dict__'):
        return {k: sanitize_payload(v) for k, v in vars(obj).items() if not str(k).startswith('_')}

    return str(obj)