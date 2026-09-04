# Runs type checking on files in this directory.
# A pytest runs pyright on the contents, raising errors on any
# non-ignored errors, and on unused errors.
# To check that something does not cause a type error, just add it to a python file
# in this folder, and a subtest will run pyright on it, with type errors causing the
# pytest to fail.
# To verify that type errors ARE raised (e.g. if checking that some overloads work as expected),
# add the hopefully offending line, appended with e.g. '# type: ignore'.
# Pyright is run so that it raise errors on unused ignores, so this will catch cases were
# we expect an error but none is raised 

import subprocess
import sys
import unittest
from pathlib import Path


def get_test_files() -> tuple[Path, ...]:
    """Gets the python file in the same fodler as this file"""
    here = Path(__file__)
    matches = here.parent.glob("*.py")
    res = tuple(p for p in matches if p != here and p.name != "__init__.py")
    return res


def check_path(path: Path) -> subprocess.CompletedProcess:
    """Runs mypy on the specified file"""
    args = [sys.executable, "-m", "pyright"]

    args.append(str(path))
    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
    )

    return result


class TestTypeErrors(unittest.TestCase):
    """This runs mypy on each file in the same directory as the test file itself.
    Any mypy errors are raised as pytest errors.
    This can be used to e.g. verify that"""

    files: tuple[Path, ...]

    def setUp(self) -> None:
        self.files = get_test_files()
        return super().setUp()

    def check(self, path: Path) -> None:
        result = check_path(path)
        msg = f"Type error in {path.name}: {result.stdout + result.stderr}"
        self.assertEqual(result.returncode, 0, msg)

    def test_files(self) -> None:
        for fn in self.files:
            with self.subTest(f"File: {fn}"):
                self.check(fn)


