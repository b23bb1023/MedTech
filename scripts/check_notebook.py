"""Check portable notebook source and reviewed public aggregate outputs."""

import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import sys


PERSONAL_PATH = re.compile(r"/(?:home|Users)/[^/\s]+|[A-Za-z]:\\+(?:Users|Documents and Settings)\\+|/tmp/ipykernel_", re.I)
SECRET = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)")
REPO_ROOT = Path(__file__).resolve().parents[1]


def output_digest(outputs):
    serialized = json.dumps(outputs, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode()).hexdigest()


def reviewed_outputs(path):
    manifest_path = REPO_ROOT / "results" / "notebook-output-manifest.json"
    if not manifest_path.is_file():
        return {}
    try:
        relative = path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return {}
    return json.loads(manifest_path.read_text())["notebooks"].get(relative, {})


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from strings(key)
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def check(path, clear=False):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    if clear:
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                cell["outputs"] = []
                cell["execution_count"] = None
            cell["metadata"] = {k: v for k, v in cell.get("metadata", {}).items() if k == "tags"}
        notebook["metadata"].pop("widgets", None)
        notebook["metadata"]["kernelspec"] = {
            "display_name": "Python 3", "language": "python", "name": "python3"
        }
        path.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    errors = []
    reviewed = reviewed_outputs(path)
    if notebook.get("nbformat") != 4:
        errors.append("Expected notebook format 4.")
    if not any(c["cell_type"] == "markdown" for c in notebook["cells"]):
        errors.append("Notebook needs explanatory markdown.")
    for i, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            if cell.get("execution_count") is not None:
                errors.append(f"Cell {i}: clear execution counts before committing.")
            outputs = cell.get("outputs", [])
            if outputs:
                expected = reviewed.get(cell.get("id"))
                if expected != output_digest(outputs):
                    errors.append(f"Cell {i}: output is new or changed; privacy review or clearing required.")
                if any(o.get("output_type") != "stream" or o.get("name") != "stdout" for o in outputs):
                    errors.append(f"Cell {i}: only reviewed aggregate stdout is permitted.")
            try:
                ast.parse("".join(cell["source"]))
            except SyntaxError as exc:
                errors.append(f"Cell {i}: invalid Python syntax ({exc.msg}).")
        if cell.get("attachments"):
            errors.append(f"Cell {i}: review embedded attachments before sharing.")
    if any(PERSONAL_PATH.search(value) for value in strings(notebook)):
        errors.append("Notebook contains a personal or local kernel path.")
    if any(SECRET.search(value) for value in strings(notebook)):
        errors.append("Notebook contains a possible credential or private key.")
    try:
        import nbformat
    except ImportError:
        print("nbformat unavailable: using JSON, syntax, output-review, and path checks.")
    else:
        try:
            nbformat.validate(notebook)
        except nbformat.ValidationError as exc:
            errors.append(f"Notebook schema validation failed: {exc.message}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Notebook checks passed: {path.name}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, help="Check one notebook; default checks all repository notebooks.")
    parser.add_argument("--clear", action="store_true", help="Clear saved outputs and execution metadata first.")
    args = parser.parse_args()
    paths = [args.path] if args.path else [REPO_ROOT / "MedTech.ipynb", *sorted((REPO_ROOT / "notebooks").glob("*.ipynb"))]
    raise SystemExit(max(check(path, args.clear) for path in paths))
