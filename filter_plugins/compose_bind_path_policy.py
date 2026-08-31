from __future__ import annotations

import posixpath
from collections.abc import Iterable
from typing import Any

from ansible.errors import AnsibleFilterError


def compose_bind_paths_outside_roots(
    paths: Iterable[Any], allowed_roots: Iterable[Any]
) -> list[str]:
    """Return normalized paths that are not within an allowed root."""
    normalized_roots = [_absolute_path(root, "allowed root") for root in allowed_roots]
    outside_roots: list[str] = []

    for path in paths:
        normalized_path = _absolute_path(path, "bind source")
        if not any(
            normalized_path == root or normalized_path.startswith(f"{root}/")
            for root in normalized_roots
        ):
            outside_roots.append(normalized_path)

    return outside_roots


def compose_bind_paths_parent_first(paths: Iterable[Any]) -> list[str]:
    """Return normalized paths ordered from shallowest to deepest."""
    normalized_paths = [_absolute_path(path, "bind source") for path in paths]
    return sorted(normalized_paths, key=lambda path: path.count("/"))


def _absolute_path(value: Any, description: str) -> str:
    if not isinstance(value, str) or not value.startswith("/"):
        raise AnsibleFilterError(f"Compose {description} must be an absolute path")
    return posixpath.normpath(value)


class FilterModule:
    def filters(self) -> dict[str, Any]:
        return {
            "compose_bind_paths_outside_roots": compose_bind_paths_outside_roots,
            "compose_bind_paths_parent_first": compose_bind_paths_parent_first,
        }
