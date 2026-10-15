"""Streamlit interface for the PawPal+ domain model."""

from datetime import date, time

import streamlit as st

from main import create_demo_owner
from pawpal_system import Owner, Pet, Scheduler, Task


def task_rows(tasks: list[Task], owner: Owner) -> list[dict]:
    """Convert domain objects to readable table rows."""
    return [
        {
            "Date": task.due_date.isoformat(),
            "Time": task.time,
            "Pet": owner.get_pet(task.pet_id).name,
            "Task": task.description,
            "Minutes": task.duration_minutes,
            "Priority": {"high": "🔴 High", "medium": "🟠 Medium", "low": "🟢 Low"}[
                task.priority
            ],
            "Repeats": task.frequency.title(),
            "Status": "✅ Done" if task.completed else "○ Pending",
        }
        for task in tasks
    ]


def notify(message: str) -> None:
    """Keep a success message visible after a widget-triggered rerun."""
    st.session_state.notice = message
    st.rerun()


st.set_page_config(page_title="PawPal+ | Care, together", page_icon="🐾", layout="wide")

if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)

with st.sidebar:
    st.title("🐾 PawPal+")
    st.caption("A little structure. A lot of care.")
    with st.form("owner_form"):
        owner_name = st.text_input("Owner name", value=owner.name)
        if st.form_submit_button("Save owner"):
            if owner_name.strip():
                owner.name = owner_name.strip()
                notify("Owner details saved.")
            else:
                st.error("Owner name is required.")
    st.subheader("Your pets")
    for pet in owner.pets:
        st.write(
            f"{'🐶' if pet.species == 'dog' else '🐱' if pet.species == 'cat' else '🐾'} {pet.name}"
        )
        st.caption(f"{pet.species.title()} · {pet.breed or 'Breed not specified'}")
    with st.expander("Add a pet", expanded=not owner.pets):
        with st.form("pet_form", clear_on_submit=True):
            pet_name = st.text_input("Pet name")
            species = st.selectbox("Species", ["dog", "cat", "other"])
            breed = st.text_input("Breed (optional)")
            if st.form_submit_button("Add pet", type="primary"):
                try:
                    owner.add_pet(Pet(pet_name, species, breed=breed.strip()))
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    notify(f"{pet_name.strip()} joined your household.")
    if not owner.pets and st.button("Load example household"):
        st.session_state.owner = create_demo_owner(date.today())
        notify("Example household loaded: Mochi and Luna.")
    st.divider()
    st.caption(
        "Your data stays available during this session. Reloading the browser or restarting the app starts a new household."
    )

st.title("Care, together.")
st.write(f"Welcome, {owner.name}. Keep every pet's routine in one place.")
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))

today_tasks = scheduler.filter_tasks(on_date=date.today())
pending = [task for task in today_tasks if not task.completed]
col1, col2, col3 = st.columns(3)
col1.metric("Pets in your care", len(owner.pets))
col2.metric("Pending today", len(pending))
col3.metric("Completed today", len(today_tasks) - len(pending))

if not owner.pets:
    st.info(
        "Add your first pet in the sidebar, or load the example household to explore."
    )
    st.stop()

with st.expander("＋ Schedule a task", expanded=not owner.get_all_tasks()):
    with st.form("task_form", clear_on_submit=True):
        pet_id = st.selectbox(
            "Pet",
            [p.id for p in owner.pets],
            format_func=lambda pid: owner.get_pet(pid).name,
        )
        description = st.text_input("Task description", placeholder="e.g. Morning walk")
        a, b, c = st.columns(3)
        due_date = a.date_input("Due date", value=date.today())
        due_time = b.time_input("Time", value=time(9, 0))
        frequency = c.selectbox("Frequency", ["once", "daily", "weekly"])
        a, b = st.columns(2)
        duration = a.number_input(
            "Duration (minutes)", min_value=1, max_value=1440, value=15
        )
        priority = b.selectbox("Priority", ["low", "medium", "high"], index=1)
        if st.form_submit_button("Add task", type="primary"):
            try:
                task = Task(
                    description,
                    due_time.strftime("%H:%M"),
                    due_date,
                    frequency,
                    duration_minutes=int(duration),
                    priority=priority,
                )
                owner.get_pet(pet_id).add_task(task)
            except ValueError as exc:
                st.error(str(exc))
            else:
                notify("Task scheduled.")

st.subheader("Your schedule")
a, b, c = st.columns(3)
selected_date = a.date_input("Schedule date", value=date.today())
pet_filter = b.selectbox("Filter by pet", ["All pets"] + [p.name for p in owner.pets])
status_filter = c.selectbox("Status", ["Pending", "All", "Completed"])
all_dates = st.checkbox("All dates", value=False)
on_date = None if all_dates else selected_date
status = {"Pending": False, "Completed": True, "All": None}[status_filter]
visible_tasks = scheduler.filter_tasks(
    pet_name=None if pet_filter == "All pets" else pet_filter,
    completed=status,
    on_date=on_date,
)

for warning in scheduler.detect_conflicts(on_date=on_date):
    st.warning(warning + ". Edit a task's time below to spread out care.")
if visible_tasks:
    st.table(task_rows(visible_tasks, owner))
else:
    st.info("No tasks match these filters. Try another date or schedule a new task.")

pending_tasks = scheduler.filter_tasks(completed=False)
if pending_tasks:
    with st.expander("Manage a task · edit or complete"):
        selected_id = st.selectbox(
            "Choose task",
            [t.id for t in pending_tasks],
            format_func=lambda tid: next(
                f"{t.due_date} {t.time} · {owner.get_pet(t.pet_id).name} · {t.description}"
                for t in pending_tasks
                if t.id == tid
            ),
        )
        selected = next(t for t in pending_tasks if t.id == selected_id)
        with st.form(f"edit_{selected.id}"):
            new_description = st.text_input(
                "Edit description", value=selected.description
            )
            a, b = st.columns(2)
            new_date = a.date_input("Edit due date", value=selected.due_date)
            new_time = b.time_input(
                "Edit time", value=time.fromisoformat(selected.time)
            )
            a, b, c = st.columns(3)
            new_duration = a.number_input(
                "Edit duration",
                min_value=1,
                max_value=1440,
                value=selected.duration_minutes,
            )
            priorities = ["low", "medium", "high"]
            new_priority = b.selectbox(
                "Edit priority", priorities, index=priorities.index(selected.priority)
            )
            frequencies = ["once", "daily", "weekly"]
            new_frequency = c.selectbox(
                "Edit frequency",
                frequencies,
                index=frequencies.index(selected.frequency),
            )
            if st.form_submit_button("Save changes"):
                try:
                    owner.get_pet(selected.pet_id).update_task(
                        selected.id,
                        description=new_description,
                        time=new_time.strftime("%H:%M"),
                        due_date=new_date,
                        duration_minutes=int(new_duration),
                        priority=new_priority,
                        frequency=new_frequency,
                    )
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    notify("Task updated.")
        if st.button("Mark complete", type="primary"):
            next_task = scheduler.mark_task_complete(selected.id)
            message = "Task completed."
            if next_task:
                message += (
                    f" Next occurrence: {next_task.due_date} at {next_task.time}."
                )
            notify(message)

with st.expander("Build a daily plan"):
    st.caption(
        f"Plan for {selected_date}. Considers every pet, selects high priority first, avoids overlapping durations, and respects your total care budget."
    )
    budget = st.number_input(
        "Available care time (minutes)", min_value=0, max_value=1440, value=60
    )
    if st.button("Generate schedule"):
        st.session_state.plan_requested = True
    if st.session_state.get("plan_requested"):
        plan, skipped = scheduler.build_plan(selected_date, int(budget))
        if plan:
            st.table(task_rows(plan, owner))
            st.success(
                f"{sum(t.duration_minutes for t in plan)} of {budget} minutes planned. Selected by priority, shown in chronological order."
            )
        else:
            st.info("No pending tasks fit this date and budget.")
        for reason in skipped:
            st.warning(reason)
        st.caption(
            "Skipped tasks remain pending. Review them before deciding what to reschedule."
        )
