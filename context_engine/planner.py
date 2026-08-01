from schemas.task import Task


TASK_CONTEXT_MAP = {
    "rate_limiting": [
        "endpoint_implementation",
        "middleware",
        "api_documentation",
        "security_policy",
        "configuration"
    ],
    "authentication": [
        "endpoint_implementation",
        "middleware",
        "api_documentation",
        "security_policy"
    ],
    "default": [
        "endpoint_implementation",
        "api_documentation"
    ]
}


def plan_context(task: Task) -> list[str]:
    task_type = task.metadata.task_type
    return TASK_CONTEXT_MAP.get(task_type, TASK_CONTEXT_MAP["default"])
