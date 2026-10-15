# PawPal+ requirements audit

Checked against the [Week 5 project instructions](https://courses.codepath.org/courses/ai110/unit/5#!projects) and [Project 2 rubric](https://courses.codepath.org/courses/ai110/pages/grading#heading-project-2-pawpal).

The technical deliverables are implemented. The personal reflection still needs student review, and the assignment has not been submitted. This is an implementation audit, not a guaranteed grade.

## Required rubric items

| Rubric item | Status | Evidence |
| --- | --- | --- |
| UML includes Owner, Pet, Task, Scheduler as Mermaid source | Pass | `diagrams/uml_final.mmd` and `diagrams/uml.mmd` |
| Each class lists attributes and methods | Pass | Final UML lists each class's public data and operations. |
| UML shows Owner–Pet and Pet–Task relationships | Pass | One-to-many composition relationships in final UML. |
| UML agrees with final implementation | Pass | Compared the diagram with dataclass fields and methods in `pawpal_system.py`. |
| Task has description, due date/time, status, and a method | Pass | `Task` fields and `mark_complete()`. |
| Pet has identity and task management | Pass | `Pet.add_task()`, `list_tasks()`, `update_task()`. |
| Owner has identity, pets, and management methods | Pass | `Owner.add_pet()`, `get_pet()`, `get_all_tasks()`. |
| Scheduler works across multiple pets | Pass | Retrieves tasks through `Owner.get_all_tasks()`; tested with multiple pets and a pet added after scheduler creation. |
| At least two algorithmic features | Pass | Chronological sorting, combined filtering, conflict warnings, recurrence, priority ranking, budget/overlap planning. |
| Features are reproducible and correct for documented behavior | Pass | Behavioral tests and deterministic CLI example in README. |
| Algorithms operate across multiple pets | Pass | Multi-pet sorting, filtering, warning, and planning tests. |
| CLI creates one Owner, two Pets, and 3+ Tasks | Pass | `create_demo_owner()` creates Jordan, Mochi, Luna, and five tasks. |
| CLI demonstrates a scheduler algorithm | Pass | Demonstrates sorting, filtering, conflicts, priority, budget planning, recurrence. |
| CLI output is readable and copied into README | Pass | Fixed-width tables and the fenced Sample Output section. |
| Pytest suite exists and passes | Pass | `tests/test_pawpal.py`, `tests/test_app.py`; run `python -m pytest`. |
| At least two meaningful passing tests | Pass | 31 cases including three Streamlit integration tests. |
| README explains classes and algorithms | Pass | Implementation summary and Smarter Scheduling sections. |
| README has demo/test commands, test coverage, passing output | Pass | Setup and run, Testing PawPal+, and Sample Output sections. |
| Reflection explains AI decisions, accepted/revised suggestions, verification | Student review needed | `reflection.md` contains a specific AI-authored implementation record. The student must review it and supply their own judgment/learning rather than presenting invented personal experiences. |

## Additional project instructions

| Requirement | Status / evidence |
| --- | --- |
| Draft UML and skeleton checkpoint | `diagrams/uml_draft.mmd`; Git commit `15f92b7`. |
| Three core user actions in reflection 1a | Register pets, schedule care, view/complete the combined schedule. |
| Python dataclasses for entities | `Task`, `Pet`, `Owner`, and `Scheduler` are dataclasses. |
| Backend independent of UI, verified through CLI | `pawpal_system.py` has no Streamlit imports; `main.py` uses it directly. |
| UI imports domain classes | `app.py` imports Owner, Pet, Scheduler, Task. |
| Session state retains the owner during interactions | Guarded initialization of `st.session_state.owner`; integration test checks repeated reruns. |
| Pet/task form submissions call backend methods | `Owner.add_pet()` and `Pet.add_task()`; integration tests submit the real forms. |
| Sorting, pet/status filtering exposed in UI | Schedule table calls `Scheduler.filter_tasks()`, which sorts results. |
| Daily/weekly recurrence creates a fresh occurrence | `Scheduler.mark_task_complete()` preserves history and prevents duplicates. |
| Daily task's next date is today + one day | Corrected during audit: uses completion date + one day, including early completion. Weekly uses + seven days. |
| Same-time conflicts warn without crashing | `Scheduler.detect_conflicts()` groups exact date/time slots; UI displays `st.warning`. |
| Tests cover completion, addition, sorting, recurrence, conflicts | Explicit cases in `tests/test_pawpal.py`; UI flow tests in `tests/test_app.py`. |
| Methods documented with docstrings | Public backend methods include one-line docstrings. |
| README documents methods, walkthrough, output, confidence | Present, including a 4/5 confidence level and limitations. |
| Reflection covers design changes, tradeoffs, AI strategy, testing | Present as a draft; student review remains required. |
| Public GitHub fork and multiple meaningful commits | `khalefa-ow/ai110-module2show-pawpal-starter`; design, implementation, testing, documentation commits. |
| Work pushed to main | Audit correction committed and pushed to the fork's main branch; local/remote SHA checked after publishing. |
| Final CodePath submission | Pending; no submission made. |

The suggested VS Code chat workflow and separate phase-specific conversations were not followed literally: implementation used the Codex app in one conversation. The reflection states that honestly. Course-page checkboxes were not changed.

Verification results: `python -m pytest` reported **31 passed in 0.85s**; Ruff reported **All checks passed!**; the README's CLI sample exactly matched fresh demo output. A source comparison confirmed that the final UML includes every public class method and that each has a docstring.

## Optional extensions

| Extension | Status |
| --- | --- |
| Advanced algorithm via agent workflow | Implemented: budget-aware selection with overlap checks; `ai_interactions.md` documents the work. |
| JSON/CSV disk persistence | Not implemented; optional. Session state is not disk persistence. |
| Priority scheduling | Implemented and shown in CLI output. |
| Professional formatting | Implemented: CLI tables, emoji status/priority, Streamlit metrics and messages. |
| Two-model/prompt comparison | Not attempted; optional. |
