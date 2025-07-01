from typing import Dict, Any, List


def get_observation(total_beats: int, tool_name: str, success: bool, message: str) -> str:
    """Generate a standardized observation string for narrative tools."""
    result = "" if success else "Error,"
    observation = (
        f"Result of '{tool_name}': {result} {message}"
    )
    print(observation)
    return observation


def _format_nested_dict(data: Dict[str, Any], indent: int = 0) -> List[str]:
    """Pretty-print a nested dictionary with clean indentation."""
    lines: List[str] = []
    indent_str = "    " * indent

    for key, value in data.items():
        display_key = str(key).replace("_", " ").capitalize()
        if isinstance(value, dict):
            lines.append(f"{indent_str}{display_key}:")
            lines.extend(_format_nested_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{indent_str}{display_key}:")
            if not value:
                lines.append(f"{indent_str}    (None)")
            else:
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"{indent_str}    -")
                        lines.extend(_format_nested_dict(item, indent + 2))
                    else:
                        lines.append(f"{indent_str}    - {item}")
        elif value is None or value == "":
            lines.append(f"{indent_str}{display_key}: (None)")
        else:
            lines.append(f"{indent_str}{display_key}: {value}")

    return lines
