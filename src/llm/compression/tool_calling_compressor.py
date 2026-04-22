def compress_tool_output(tool_name: str, raw_output: str, max_chars = 1500) -> str:
    length = len(raw_output)

    if length <= max_chars:
        return raw_output

    if tool_name in ["web_search"]:
        return f"{raw_output[:max_chars]}\n\n... [{length - max_chars} chars truncated.]"

    if tool_name in ["read_file", "code_interpreter"]:
        meta_chars = int(max_chars * 0.4)

        head = raw_output[:meta_chars]
        tail = raw_output[-meta_chars:]
        truncated_count = length - (meta_chars * 2)

        return f"{head}\n\n... [{truncated_count} chars truncated] ...\n\n{tail}"

    half = max_chars / 2
    return f"{raw_output[:half]}\n\n... [{length - max_chars} chars truncated] ...\n\n{raw_output[-half:]}"