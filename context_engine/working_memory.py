from schemas.working_memory import WorkingMemory


def create_working_memory() -> WorkingMemory:
    return WorkingMemory()


def reset_working_memory(memory: WorkingMemory) -> None:
    memory.clear()
