"""Run a reproducible CLI demonstration: python main.py --date 2026-10-14."""

import argparse
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def create_demo_owner(day: date) -> Owner:
    """Build two pets with deliberately unordered tasks and one conflicting time."""
    owner = Owner("Jordan")
    mochi, luna = Pet("Mochi", "dog", breed="Golden Retriever"), Pet("Luna", "cat")
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(
        Task("Evening walk", "18:00", day, "daily", duration_minutes=30, priority="low")
    )
    luna.add_task(
        Task("Medication", "09:00", day, "weekly", duration_minutes=5, priority="high")
    )
    mochi.add_task(
        Task("Breakfast", "08:00", day, "daily", duration_minutes=10, priority="high")
    )
    mochi.add_task(Task("Morning walk", "09:00", day, "daily", duration_minutes=30))
    luna.add_task(Task("Enrichment", "14:00", day, duration_minutes=20, priority="low"))
    return owner


def print_tasks(title: str, tasks: list[Task], owner: Owner) -> None:
    """Print a readable schedule table without extra dependencies."""
    print(f"\n{title}")
    print(f"{'Time':<7} {'Pet':<8} {'Task':<18} {'Min':>3}  {'Priority':<8} Status")
    print("-" * 66)
    for task in tasks:
        status = "Done" if task.completed else "Pending"
        print(
            f"{task.time:<7} {owner.get_pet(task.pet_id).name:<8} "
            f"{task.description:<18} {task.duration_minutes:>3}  {task.priority:<8} {status}"
        )


def main() -> None:
    """Demonstrate multi-pet sorting, filtering, warnings, planning, and recurrence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    day = parser.parse_args().date
    owner = create_demo_owner(day)
    scheduler = Scheduler(owner)
    print(f"PawPal+ | {owner.name}'s household | {day}")
    print_tasks("Today's Schedule (chronological)", scheduler.sort_by_time(), owner)
    for warning in scheduler.detect_conflicts(on_date=day):
        print(f"WARNING: {warning}")
    print_tasks(
        "Luna's pending tasks",
        scheduler.filter_tasks(pet_name="Luna", completed=False),
        owner,
    )
    print_tasks(
        "Priority order (high first, then time)", scheduler.sort_by_priority(), owner
    )
    plan, skipped = scheduler.build_plan(day, available_minutes=45)
    print_tasks("45-minute plan (priority selection, displayed by time)", plan, owner)
    for reason in skipped:
        print(f"Skipped: {reason}")
    breakfast = next(t for t in owner.get_all_tasks() if t.description == "Breakfast")
    next_task = scheduler.mark_task_complete(breakfast.id, completed_on=day)
    print(
        f"\nCompleted Breakfast for Mochi; next daily occurrence: {next_task.due_date} {next_task.time}."
    )
    print(
        f"Completing the same occurrence again adds no task: {scheduler.mark_task_complete(breakfast.id, day) is None}."
    )


if __name__ == "__main__":
    main()
