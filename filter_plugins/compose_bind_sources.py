from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ansible.errors import AnsibleFilterError


def compose_bind_sources(compose: Any) -> list[str]:
    """Return unique bind sources declared by Compose services."""
    if not isinstance(compose, Mapping):
        raise AnsibleFilterError("Compose content must be a mapping")

    services = compose.get("services", {})
    if not isinstance(services, Mapping):
        raise AnsibleFilterError("Compose 'services' must be a mapping")

    sources: list[str] = []
    for service_name, service in services.items():
        if not isinstance(service, Mapping):
            raise AnsibleFilterError(
                f"Compose service {service_name!r} must be a mapping"
            )

        volumes = service.get("volumes", [])
        if not isinstance(volumes, list):
            raise AnsibleFilterError(
                f"Compose service {service_name!r} volumes must be a list"
            )

        for volume in volumes:
            source = _bind_source(volume, str(service_name))
            if source is not None and source not in sources:
                sources.append(source)

    return sources


def _bind_source(volume: Any, service_name: str) -> str | None:
    if isinstance(volume, str):
        source, separator, _ = volume.partition(":")
        if not separator:
            return None
        return source if _looks_like_bind_path(source) else None

    if not isinstance(volume, Mapping):
        raise AnsibleFilterError(
            f"Compose service {service_name!r} has an invalid volume entry"
        )

    if volume.get("type") != "bind":
        return None

    source = volume.get("source")
    if not isinstance(source, str) or not source:
        raise AnsibleFilterError(
            f"Compose service {service_name!r} has a bind mount without a source"
        )
    return source


def _looks_like_bind_path(source: str) -> bool:
    return source.startswith("/") or source.startswith("./") or source.startswith("../")


class FilterModule:
    def filters(self) -> dict[str, Any]:
        return {"compose_bind_sources": compose_bind_sources}
