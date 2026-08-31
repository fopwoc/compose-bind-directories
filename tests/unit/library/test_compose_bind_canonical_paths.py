from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).parents[3]
    / "library"
    / "compose_bind_canonical_paths.py"
)
SPEC = importlib.util.spec_from_file_location(
    "compose_bind_canonical_paths", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ComposeBindCanonicalPathsTest(unittest.TestCase):
    def test_resolves_symlinked_nearest_existing_ancestor(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            allowed_root = root / "allowed"
            outside_root = root / "outside"
            allowed_root.mkdir()
            outside_root.mkdir()
            (allowed_root / "link").symlink_to(outside_root, target_is_directory=True)

            result = MODULE.resolve_path(str(allowed_root / "link" / "app"))

            self.assertEqual(
                result["nearest_existing_ancestor"], str(allowed_root / "link")
            )
            self.assertEqual(
                result["canonical_path"], str(outside_root.resolve() / "app")
            )

    def test_reattaches_all_missing_path_parts(self) -> None:
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)

            result = MODULE.resolve_path(str(root / "app" / "cache"))

            self.assertEqual(result["nearest_existing_ancestor"], str(root))
            self.assertEqual(
                result["canonical_path"], str(root.resolve() / "app" / "cache")
            )


if __name__ == "__main__":
    unittest.main()
