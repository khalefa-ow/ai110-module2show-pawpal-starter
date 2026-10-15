# AI Interactions Log

## Agent Workflow

**Tool:** Codex, in this project's conversation. No subagents or second models were used.

**Actual user request:** “Go to https://courses.codepath.org/courses/ai110/unit/5#!projects and implement the steps there.”

**Work completed:** Read the authenticated course page and rubric; retrieved the starter; created draft UML and skeletons; implemented four dataclasses and household-wide algorithms; connected Streamlit forms to the model; added the CLI and pytest/AppTest suites; ran verification; and prepared documentation.

**Optional algorithmic extension:** `Scheduler.build_plan()` greedily chooses higher-priority tasks within an available-minute budget and rejects overlapping selected intervals. It returns explanations for skipped tasks. `sort_by_priority()` ranks high/medium/low with time as a tie breaker. The CLI shows both priority order and a 45-minute plan, while Streamlit exposes a budget input and **Generate schedule** action.

**Files modified:** `pawpal_system.py` (classes and algorithms), `main.py` (reproducible demo and formatting), `app.py` (forms, filters, completion, editing, planning), `tests/test_pawpal.py` and `tests/test_app.py` (behavior and integration verification), `diagrams/*.mmd` (architecture), `.streamlit/config.toml` (theme), `requirements.txt`, `pytest.ini`, `ruff.toml`, `.gitignore`, `README.md`, `reflection.md`, and this log.

**Corrections during agent verification:** The first test run reached 29 passing cases and timed out on the first table-rendering UI integration under AppTest's three-second default. The harness now allows 15 seconds; subsequent full runs passed in under a second. Ruff fixed import organization. No manual student corrections are claimed.

**Verification:** CLI output is captured in README; 30 pytest cases pass, including multi-pet selection, a zero budget, overlapping versus adjacent tasks, and a live Streamlit widget workflow. Browser inspection verified the populated household and conflict warning.

**Publishing adjustment:** An optional GitHub Actions workflow was omitted because the existing GitHub token lacks workflow permissions. Local verification remains available with `python -m pytest`. Browser review also led to moving the **All dates** checkbox below the filter columns so its label remains readable at narrower window widths.

## Output formatting

`main.print_tasks()` uses Python formatted strings for aligned columns. `app.task_rows()` provides emoji priority/status indicators to `st.table`; `st.metric`, `st.success`, and `st.warning` distinguish totals, completed actions, and scheduling concerns. README describes these functions and the example workflow.

## Scope of claims

The optional persistence and two-model comparison exercises were not attempted. The reflection is an AI-authored implementation record for the student to review and personalize; it does not fabricate personal learning experiences or prompts from other chat sessions.
