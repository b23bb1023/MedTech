"""Check portable notebook source and require a clean public artifact."""

import argparse
import ast
import json
from pathlib import Path
import re
import sys


PERSONAL_PATH = re.compile(r"/(?:home|Users)/[^/\s]+|[A-Za-z]:\\+(?:Users|Documents and Settings)\\+|/tmp/ipykernel_", re.I)


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
    if notebook.get("nbformat") != 4:
        errors.append("Expected notebook format 4.")
    if not any(c["cell_type"] == "markdown" for c in notebook["cells"]):
        errors.append("Notebook needs explanatory markdown.")
    for i, cell in enumerate(notebook["cells"]):
        if cell["cell_type"] == "code":
            if cell.get("outputs") or cell.get("execution_count") is not None:
                errors.append(f"Cell {i}: clear outputs and execution count before committing.")
            try:
                ast.parse("".join(cell["source"]))
            except SyntaxError as exc:
                errors.append(f"Cell {i}: invalid Python syntax ({exc.msg}).")
        if cell.get("attachments"):
            errors.append(f"Cell {i}: review embedded attachments before sharing.")
    if any(PERSONAL_PATH.search(value) for value in strings(notebook)):
        errors.append("Notebook contains a personal or local kernel path.")
    try:
        import nbformat
    except ImportError:
        print("nbformat unavailable: using JSON, syntax, output, and path checks.")
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
    parser.add_argument("path", nargs="?", type=Path, default=Path("MedTech.ipynb"))
    parser.add_argument("--clear", action="store_true", help="Clear saved outputs and execution metadata first.")
    args = parser.parse_args()
    raise SystemExit(check(args.path, args.clear))
