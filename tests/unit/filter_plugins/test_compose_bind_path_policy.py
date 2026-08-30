from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

from ansible.errors import AnsibleFilterError


PLUGIN_PATH = (
    Path(__file__).parents[3]
    / "filter_plugins"
    / "compose_bind_path_policy.py"
)
SPEC = importlib.util.spec_from_file_location("compose_bind_path_policy", PLUGIN_PATH)
assert SPEC is not None and SPEC.loader is not None
PLUGIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLUGIN)


class ComposeBindPathPolicyTest(unittest.TestCase):
    def test_accepts_roots_and_descendants_after_normalization(self) -> None:
        self.assertEqual(
            PLUGIN.compose_bind_paths_outside_roots(
                ["/mnt/data", "/mnt/data/app/../cache", "/mnt/fast/app"],
                ["/mnt/data/", "/mnt/fast"],
            ),
            [],
        )

    def test_rejects_paths_with_only_a_common_prefix(self) -> None:
        self.assertEqual(
            PLUGIN.compose_bind_paths_outside_roots(
                ["/mnt/database", "/srv/app"], ["/mnt/data"]
            ),
            ["/mnt/database", "/srv/app"],
        )

    def test_rejects_non_absolute_inputs(self) -> None:
        with self.assertRaisesRegex(AnsibleFilterError, "absolute path"):
            PLUGIN.compose_bind_paths_outside_roots(["relative"], ["/mnt/data"])


if __name__ == "__main__":
    unittest.main()
