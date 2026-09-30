"""Public artifact checks, including recovery after local notebook execution."""

from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.check_notebook import check


class NotebookTests(unittest.TestCase):
    def test_public_notebook_is_clean(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(check(Path("MedTech.ipynb")), 0)

    def test_execution_outputs_are_rejected_and_can_be_cleared(self):
        notebook = json.loads(Path("MedTech.ipynb").read_text())
        cell = next(c for c in notebook["cells"] if c["cell_type"] == "code")
        cell["execution_count"] = 1
        cell["outputs"] = [{"output_type": "stream", "name": "stdout", "text": ["Local preview\n"]}]
        with tempfile.TemporaryDirectory(dir=".") as temporary:
            path = Path(temporary) / "executed.ipynb"
            path.write_text(json.dumps(notebook))
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(check(path), 1)
                self.assertEqual(check(path, clear=True), 0)

    def test_personal_path_in_source_is_rejected_even_after_clearing(self):
        notebook = json.loads(Path("MedTech.ipynb").read_text())
        cell = next(c for c in notebook["cells"] if c["cell_type"] == "code")
        cell["source"] = ["local_path = '/home/example_person/Downloads/data.csv'\n"]
        with tempfile.TemporaryDirectory(dir=".") as temporary:
            path = Path(temporary) / "local.ipynb"
            path.write_text(json.dumps(notebook))
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(check(path, clear=True), 1)

    def test_windows_and_macos_paths_are_rejected(self):
        notebook = json.loads(Path("MedTech.ipynb").read_text())
        cell = next(c for c in notebook["cells"] if c["cell_type"] == "code")
        for local_path in [r"C:\Users\example_person\Desktop\data.csv", "/Users/example_person/Desktop/data.csv"]:
            with self.subTest(path=local_path), tempfile.TemporaryDirectory(dir=".") as temporary:
                path = Path(temporary) / "local.ipynb"
                cell["source"] = [f"local_path = {local_path!r}\n"]
                path.write_text(json.dumps(notebook))
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    self.assertEqual(check(path), 1)


if __name__ == "__main__":
    unittest.main()
