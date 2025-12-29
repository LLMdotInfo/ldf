"""Shared spec utilities.

Common functions for spec name validation and other shared spec operations.
"""


def sanitize_spec_name(name: str) -> str:
    """Sanitize spec name to prevent path traversal.

    Args:
        name: Spec name to sanitize

    Returns:
        The validated spec name

    Raises:
        ValueError: If the name contains path traversal attempts
    """
    if ".." in name or name.startswith("/") or name.startswith("\\"):
        raise ValueError(f"Invalid spec name: {name}")
    if "/" in name or "\\" in name:
        raise ValueError(f"Spec name cannot contain path separators: {name}")
    return name
