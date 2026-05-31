SOURCE_REGISTRY_ROW_NOT_FOUND = "source_data_registry row not found"
SOURCE_DEPENDENCY_ROLE_READ = "read"
SOURCE_EMPTY_CHANGE_SEQ = 0
SOURCE_INITIAL_CHANGE_SEQ = 1


def source_registry_row_not_found(identifier: object) -> str:
    return f"{SOURCE_REGISTRY_ROW_NOT_FOUND}: {identifier}"


__all__ = [
    "SOURCE_DEPENDENCY_ROLE_READ",
    "SOURCE_EMPTY_CHANGE_SEQ",
    "SOURCE_INITIAL_CHANGE_SEQ",
    "SOURCE_REGISTRY_ROW_NOT_FOUND",
    "source_registry_row_not_found",
]
