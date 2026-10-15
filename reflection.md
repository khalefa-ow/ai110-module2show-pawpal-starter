# PawPal+ Project Reflection

> AI-authored implementation reflection based on this repository and the actual development session. The student should review and personalize it before submission. It does not claim that the student personally made edits, used separate chats, or compared models.

## 1. System Design

### a. Initial design

Three core user actions are: register pets in one household; schedule each pet's care with a due date/time; and see a combined daily schedule and complete activities.

The draft UML in `diagrams/uml_draft.mmd` assigns one responsibility to each of four classes. `Owner` manages pets and aggregates all their tasks. `Pet` holds identifying details and activities. `Task` represents one occurrence with description, time, due date, frequency, and completion status. `Scheduler` depends on `Owner`, so its results include every pet rather than a snapshot of one pet's list. Dataclasses provide explicit fields and independent list factories.

### b. Design changes

The final implementation adds stable task/pet IDs, task duration and priority, editing, and a `pet_id` link set by `Pet.add_task()`. These let the UI select a specific occurrence even when descriptions or times match. The scheduler owns recurrence because creating a new occurrence requires access to its pet; `Task.mark_complete()` remains a simple status operation. The final diagram in `diagrams/uml_final.mmd` includes the added methods and fields.

The review also added duplicate-name checks and validated task replacement: an invalid edit leaves the previous task intact. These changes keep filtering unambiguous and prevent partial updates.

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and priorities

Tasks have explicit dates and zero-padded `HH:MM` times. The schedule sorts by `(due_date, time)`, while filters can combine pet, status, and date. The plan builder considers only pending tasks for the selected day, tries high before medium before low priority, then breaks ties by time. It uses the owner's total available care minutes and avoids overlapping selected intervals across all pets. Skipped tasks remain pending with explanations.

Daily and weekly recurrence use `timedelta`. The next due date is the completion date plus one or seven days, matching the course instructions. A requirements audit revised the initial policy, which had preserved the original due date for early completions. Completing the same occurrence twice produces only one next occurrence. Completed history remains visible.

### b. Tradeoffs

The lightweight warning checks exact date/start-time collisions with a dictionary of slots. It is easy to explain and avoids pairwise duplicate warnings, but does not flag every possible duration overlap. The optional plan builder does check duration overlaps among tasks it selects.

Planning is greedy rather than globally optimal: choosing one long, high-priority activity can leave less room for several shorter activities. This is reasonable for a small household and transparent priorities, but it is not a guarantee that all essential care fits. The app explicitly lists skipped tasks so the owner can reschedule them. Overnight overlaps, multiple caregivers, time zones, and medical urgency rules are outside the implemented scope.

Session state keeps the model alive across interactions without introducing database setup. That simplicity costs persistence across browser reloads and app restarts; the sidebar and README explain this limitation.

## 3. AI Collaboration

### a. How AI was used

The user's actual request was to open the Week 5 project page and implement its steps. Codex read the instructions and rubric in the user's authenticated browser, retrieved the official starter, drafted UML/class skeletons, implemented the backend and interface, wrote tests, ran the CLI and tests, and prepared documentation.

The useful capabilities were repository editing across related files, terminal feedback, and live-browser inspection. A change such as recurring completion required coordinated updates to `pawpal_system.py`, `main.py`, `app.py`, and tests. Concrete acceptance criteria—two pets, unsorted tasks, a shared time, and a daily completion—made verification specific.

This work used one conversation with distinct design, implementation, and verification stages. Separate chat sessions were not used, so no benefit from a separate-chat experiment is claimed. There was no second-model comparison.

### b. Judgment and verification

The implementation adopted the AI-generated four-class structure, dataclasses, standard-library date arithmetic, and stable sorting because they map directly to the required behavior.

The initial skeleton's simple completion approach was revised for the full implementation: setting a boolean alone cannot attach the next recurring task to the right pet. `Scheduler.mark_task_complete()` now creates the next occurrence and checks the old status first. Another design choice was to avoid putting a separate task list in Streamlit; the app stores an `Owner` object and calls backend methods, preventing two sources of truth.

These were implementation decisions by the AI assistant, not a claim that the student rejected an AI response personally. The concrete verification is in the pytest cases, CLI output, and browser inspection. Student-specific judgment and learning should be added after reviewing the code.

## 4. Testing and Verification

### a. What was tested

The five main verification areas are: entity relationships and validation; chronological sorting and combined filtering; completion and daily/weekly recurrence; conflict warnings across pets; and priority/budget/overlap planning. Edge cases include no tasks, duplicate names, invalid times, year and leap-day boundaries, overdue and early completion, repeated completion, adjacent intervals, and invalid edits.

Three Streamlit integration tests exercise actual widget submissions, including adding a pet, scheduling/editing/completing a task, retaining session data after reruns, filtering the example household, generating a plan, and rejecting a blank pet name. The first full run passed 29 tests but hit the default three-second AppTest timeout when rendering the first table. The test harness allows 15 seconds for UI initialization; the next complete run passed in under a second. The timeout change did not change scheduler behavior or reduce assertions.

The CLI was run with a fixed date (`python main.py --date 2026-10-14`) so the documented output is reproducible. A live browser check confirmed the example's two pets, chronological table, and conflict warning. The requirements audit expanded early-completion coverage to both daily and weekly tasks: all 31 tests passed in 0.85 seconds, and Ruff reported that all checks passed. A fresh CLI run exactly matched the README sample output.

### b. Confidence

Implementation confidence is 4/5 for the documented, single-session scope. Tests verify required behavior and representative edge cases but do not prove correctness for every workload. Future verification should include browser automation at narrow widths, overnight tasks across dates, sustained large histories, and persistent storage/recovery if that extension is added.

## 5. Reflection

### a. What went well

The backend is usable without Streamlit, and the CLI exposes scheduling decisions as readable text. The UI calls the same methods covered by the tests, making it easier to relate what a user sees to the actual model behavior.

### b. What could improve

The next iteration could introduce explicit JSON import/export or local persistence, duration-overlap warnings for the full schedule, and a choice of recurrence policies for overdue weekly tasks. A larger planning system should model caregiver availability and essential tasks separately from an ordinary priority label.

### c. Key takeaway

The lead architect's role is to define relationships and acceptance criteria, evaluate generated code against observable examples, and keep claims within the evidence. A generated class diagram or passing happy-path test alone is not enough; the model, UI, recurrence rules, and documentation must agree.
