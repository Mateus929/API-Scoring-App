# OpenAPI Spec Scorer

## Overview

This tool scores OpenAPI 3.x specification files (YAML or JSON) for quality based on various criteria.

---

## Features

- Scores OpenAPI 3.x specs based on customizable quality rules.
- Outputs results in JSON, Markdown, or HTML.
- Easily extensible: add new scoring rules with minimal effort.
- CLI designed for simplicity and usability.


---

## Setup

1. Clone the repository:

```bash
git https://github.com/Mateus929/API-Scoring-App.git
cd API-Scoring-App
```

2. Create and activate a Python virtual environment:

```bash
python3 -m venv env
source env/bin/activate 
```

3. Install dependencies:

```bash
make install
```

---

## Usage

Run the CLI tool on an OpenAPI spec file or URL:

```bash
poetry run python -m src.cli <input_path> [--export json|markdown|html] [--output <output_file>]
```

Example exporting as markdown:

```bash
poetry run python -m src.cli openapi.yaml --export markdown --output report.md
```

If no `--output` is specified, a default file `report.<ext>` will be created. If no `--export` is specified, program just prints overall score.

---

## Development

- The main CLI entry point is `src/cli.py`.
- The scoring logic resides in the `src/scoring/` directory. Each rule is implemented as a separate module. Refer to the `Rule` interface in `src/scoring/rule_base.py` for detailed documentation.
- The `ScoringEngine` class in `src/core/scoring_engine.py` computes the overall score and returns a dictionary of individual rule scores and issues.
- Report export (i.e., converting the score dictionary into a specific format) is handled by `src/reports/export.py`.
- All tests are located in the `tests/` directory:
  - Unit tests for each rule are in `tests/unit_tests/`.
  - Integration tests for the CLI and export formats are in `tests/test_cli_score.py`, using files from `tests/test_files/`.

To run the full test suite:

```bash
poetry run pytest
```
---

## Design Decisions

- The project is built around a simple and minimal approach to validation and scoring, focusing on what’s most important.
- It supports multiple export formats (like JSON, Markdown, and HTML), making it easy to integrate into other tools or workflows.
- We use [Click](https://click.palletsprojects.com/) to provide a clean and user-friendly command-line interface.
- [Pytest](https://docs.pytest.org/) is used for testing — including running the CLI and checking if it works correctly with different inputs and outputs.


## Sample run

Run the tool on a sample OpenAPI file:

```bash
poetry run python -m src.cli tests/test_files/file_35_50.json --export json
```

You should see a JSON report (`repors.json` file) with the scoring details.

---
