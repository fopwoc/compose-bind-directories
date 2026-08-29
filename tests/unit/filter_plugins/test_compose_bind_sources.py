from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from ansible.errors import AnsibleFilterError


PLUGIN_PATH = (
    Path(__file__).parents[3] / "filter_plugins" / "compose_bind_sources.py"
)
SPEC = importlib.util.spec_from_file_location("compose_bind_sources", PLUGIN_PATH)
assert SPEC is not None and SPEC.loader is not None
PLUGIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLUGIN)


class ComposeBindSourcesTest(unittest.TestCase):
    def test_extracts_unique_short_and_long_bind_sources(self) -> None:
        compose = {
            "services": {
                "app": {
                    "volumes": [
                        "/srv/app/data:/data",
                        "/srv/app/cache:/cache:rw",
                        "./config.yaml:/app/config.yaml:ro",
                        "named-data:/named",
                        {
                            "type": "bind",
                            "source": "/srv/app/uploads",
                            "target": "/uploads",
                        },
                    ]
                },
                "worker": {"volumes": ["/srv/app/data:/data"]},
            }
        }

        self.assertEqual(
            PLUGIN.compose_bind_sources(compose),
            [
                "/srv/app/data",
                "/srv/app/cache",
                "./config.yaml",
                "/srv/app/uploads",
            ],
        )

    def test_ignores_named_volumes_and_non_bind_long_syntax(self) -> None:
        compose = {
            "services": {
                "app": {
                    "volumes": [
                        "data:/data",
                        {"type": "volume", "source": "cache", "target": "/cache"},
                        {"type": "tmpfs", "target": "/run"},
                        "/anonymous-container-volume",
                    ]
                }
            }
        }

        self.assertEqual(PLUGIN.compose_bind_sources(compose), [])

    def test_rejects_bind_without_source(self) -> None:
        compose = {
            "services": {
                "app": {"volumes": [{"type": "bind", "target": "/data"}]}
            }
        }

        with self.assertRaisesRegex(AnsibleFilterError, "without a source"):
            PLUGIN.compose_bind_sources(compose)

    def test_rejects_invalid_services_shape(self) -> None:
        with self.assertRaisesRegex(AnsibleFilterError, "services.*mapping"):
            PLUGIN.compose_bind_sources({"services": []})


if __name__ == "__main__":
    unittest.main()
