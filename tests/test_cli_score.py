import os
import re
import subprocess
import json
import tempfile
from typing import Optional
import pytest

TEST_DIR = "test_files"


def extract_score(path: str, export_format: str) -> Optional[int]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    if export_format == "json":
        try:
            data = json.loads(content)
            return int(data.get("score"))
        except (ValueError, TypeError, json.JSONDecodeError):
            return None
    elif export_format == "markdown":
        match = re.search(r"\*\*Score:\*\*\s*(\d+)", content)
        if match:
            return int(match.group(1))

    elif export_format == "html":
        match = re.search(r"<strong>Score:</strong>\s*(\d+)", content)
        if match:
            return int(match.group(1))
    return None


@pytest.mark.parametrize(
    "filename",
    [f for f in os.listdir(TEST_DIR) if re.match(r"file_\d+_\d+\.(json|ya?ml)$", f)],
)
@pytest.mark.parametrize("export_format", ["json", "markdown", "html"])
def test_score_bounds(filename: str, export_format: str) -> None:
    match = re.match(r"file_(\d+)_(\d+)\.(json|ya?ml)$", filename)
    assert match is not None, f"Filename does not match expected pattern: {filename}"

    a, b = int(match.group(1)), int(match.group(2))
    input_path = os.path.join(TEST_DIR, filename)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        output_path = tmp.name

    result = subprocess.run(
        [
            "python",
            "-m",
            "src.cli",  # adjust to your CLI entry point
            input_path,
            "--export",
            export_format,
            "--output",
            output_path,
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"CLI failed for {filename}:\n{result.stderr}"
    score = extract_score(output_path, export_format)
    assert score is not None, f"Score not found in report: {output_path}"

    assert a <= score <= b, (
        f"{filename}: Score {score} not in expected range [{a}, {b}]"
    )

    os.remove(output_path)
