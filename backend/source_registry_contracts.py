SOURCE_REGISTRY_ROW_NOT_FOUND = "source_data_registry row not found"


def source_registry_row_not_found(identifier: object) -> str:
    return f"{SOURCE_REGISTRY_ROW_NOT_FOUND}: {identifier}"
