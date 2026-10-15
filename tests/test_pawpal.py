"""Behavioral tests for the four-class model and scheduling algorithms."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 10, 14)


@pytest.fixture
def household():
    """Provide an owner, two pets, and a scheduler without tasks."""
    owner = Owner("Jordan", [Pet("Mochi", "dog"), Pet("Luna", "cat")])
    return owner, owner.pets[0], owner.pets[1], Scheduler(owner)


def test_task_completion():
    task = Task("Walk", "08:00", DAY)
    assert not task.completed
    task.mark_complete()
    assert task.completed


def test_task_addition_and_independent_lists():
    first, second = Pet("Mochi", "dog"), Pet("Luna", "cat")
    task = Task("Feed", "08:00", DAY)
    first.add_task(task)
    assert first.tasks == [task]
    assert task.pet_id == first.id
    assert second.tasks == []
    first.list_tasks().clear()
    assert first.tasks == [task]


def test_sorting_across_pets_and_dates_without_mutating(household):
    owner, mochi, luna, scheduler = household
    late = Task("Walk", "18:00", DAY)
    tomorrow = Task("Groom", "07:00", DAY + timedelta(days=1))
    early = Task("Feed", "08:00", DAY)
    mochi.add_task(late)
    mochi.add_task(tomorrow)
    luna.add_task(early)
    assert scheduler.sort_by_time() == [early, late, tomorrow]
    assert mochi.tasks == [late, tomorrow]
    # A scheduler created before insertion must see newly added pets and tasks.
    third = Pet("Pip", "bird", [Task("Water", "06:00", DAY)])
    owner.add_pet(third)
    assert scheduler.sort_by_time()[0] is third.tasks[0]


def test_combined_filters(household):
    _, mochi, luna, scheduler = household
    pending = Task("Feed", "08:00", DAY)
    done = Task("Walk", "09:00", DAY, completed=True)
    future = Task("Groom", "09:00", DAY + timedelta(days=1))
    mochi.add_task(pending)
    mochi.add_task(done)
    mochi.add_task(future)
    luna.add_task(Task("Feed", "08:00", DAY))
    assert scheduler.filter_tasks("mochi", False, DAY) == [pending]
    assert scheduler.filter_tasks("Mochi", True) == [done]
    assert scheduler.filter_tasks("missing") == []


def test_empty_household(household):
    _, _, _, scheduler = household
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.build_plan(DAY, 60) == ([], [])


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7)])
@pytest.mark.parametrize("due", [date(2026, 12, 31), date(2028, 2, 28)])
def test_recurrence_preserves_details_and_history(household, frequency, days, due):
    owner, mochi, _, scheduler = household
    task = Task("Care", "08:00", due, frequency, duration_minutes=10, priority="high")
    mochi.add_task(task)
    next_task = scheduler.mark_task_complete(task.id, completed_on=due)
    assert task.completed
    assert next_task.due_date == due + timedelta(days=days)
    assert not next_task.completed
    assert next_task.id != task.id
    assert next_task.pet_id == mochi.id
    assert (
        next_task.time,
        next_task.frequency,
        next_task.priority,
        next_task.duration_minutes,
    ) == (
        "08:00",
        frequency,
        "high",
        10,
    )
    assert owner.get_all_tasks() == [task, next_task]
    assert scheduler.mark_task_complete(task.id, due) is None
    assert len(owner.get_all_tasks()) == 2


def test_overdue_recurrence_uses_completion_day(household):
    _, _, luna, scheduler = household
    task = Task("Care", "08:00", DAY - timedelta(days=4), "daily")
    luna.add_task(task)
    assert scheduler.mark_task_complete(task.id, DAY).due_date == DAY + timedelta(
        days=1
    )


def test_early_completion_preserves_future_due_date(household):
    _, mochi, _, scheduler = household
    task = Task("Care", "08:00", DAY + timedelta(days=2), "weekly")
    mochi.add_task(task)
    assert scheduler.mark_task_complete(task.id, DAY).due_date == DAY + timedelta(
        days=9
    )


def test_one_off_completion_does_not_duplicate(household):
    owner, mochi, _, scheduler = household
    task = Task("Appointment", "08:00", DAY)
    mochi.add_task(task)
    assert scheduler.mark_task_complete(task.id, DAY) is None
    assert task.completed and owner.get_all_tasks() == [task]
    with pytest.raises(ValueError, match="Task not found"):
        scheduler.mark_task_complete("missing")


def test_conflicts_group_same_and_different_pets_and_ignore_done_or_other_dates(
    household,
):
    _, mochi, luna, scheduler = household
    mochi.add_task(Task("Walk", "08:00", DAY))
    mochi.add_task(Task("Breakfast", "08:00", DAY))
    luna.add_task(Task("Feed", "08:00", DAY))
    luna.add_task(Task("Done", "08:00", DAY, completed=True))
    luna.add_task(Task("Tomorrow", "08:00", DAY + timedelta(days=1)))
    warnings = scheduler.detect_conflicts(on_date=DAY)
    assert len(warnings) == 1
    assert "Mochi: Walk" in warnings[0] and "Luna: Feed" in warnings[0]
    assert "Mochi: Breakfast" in warnings[0]
    assert "Done" not in warnings[0] and "Tomorrow" not in warnings[0]
    assert scheduler.detect_conflicts(DAY + timedelta(days=1)) == []


def test_priority_ranking_and_budget_plan(household):
    _, mochi, luna, scheduler = household
    low = Task("Play", "08:00", DAY, duration_minutes=20, priority="low")
    high = Task("Medication", "09:00", DAY, duration_minutes=10, priority="high")
    mochi.add_task(low)
    luna.add_task(high)
    assert scheduler.sort_by_priority() == [high, low]
    chosen, skipped = scheduler.build_plan(DAY, 10)
    assert chosen == [high] and len(skipped) == 1
    assert "budget" in skipped[0]
    assert not low.completed and not high.completed
    assert scheduler.build_plan(DAY, 0)[0] == []
    with pytest.raises(ValueError, match="budget"):
        scheduler.build_plan(DAY, -1)


def test_plan_rejects_overlaps_but_allows_adjacent_slots(household):
    _, mochi, luna, scheduler = household
    high = Task("Care", "09:00", DAY, duration_minutes=30, priority="high")
    overlap = Task("Walk", "09:15", DAY, duration_minutes=10)
    adjacent = Task("Feed", "09:30", DAY, duration_minutes=10)
    mochi.add_task(overlap)
    mochi.add_task(adjacent)
    luna.add_task(high)
    chosen, skipped = scheduler.build_plan(DAY, 40)
    assert chosen == [high, adjacent]
    assert len(skipped) == 1 and "overlaps" in skipped[0]


def test_plan_only_selects_pending_tasks_on_requested_day(household):
    _, mochi, _, scheduler = household
    mochi.add_task(Task("Done", "08:00", DAY, completed=True))
    mochi.add_task(Task("Tomorrow", "08:00", DAY + timedelta(days=1)))
    assert scheduler.build_plan(DAY, 60) == ([], [])


def test_edit_validates_atomically_and_preserves_identity(household):
    _, mochi, _, scheduler = household
    task = Task("Walk", "08:00", DAY)
    mochi.add_task(task)
    updated = mochi.update_task(
        task.id, description="Long walk", time="09:00", priority="high"
    )
    assert updated.id == task.id and updated.pet_id == mochi.id
    assert scheduler.sort_by_time() == [updated]
    with pytest.raises(ValueError):
        mochi.update_task(task.id, time="25:00")
    assert mochi.tasks == [updated]
    scheduler.mark_task_complete(task.id)
    with pytest.raises(ValueError, match="Completed"):
        mochi.update_task(task.id, time="10:00")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"description": " "},
        {"time": "9:00"},
        {"time": "24:00"},
        {"frequency": "monthly"},
        {"priority": "urgent"},
        {"duration_minutes": 0},
        {"duration_minutes": -1},
        {"duration_minutes": 1.5},
        {"due_date": "2026-10-14"},
    ],
)
def test_invalid_task_details(kwargs):
    fields = {"description": "Walk", "time": "08:00", "due_date": DAY}
    with pytest.raises(ValueError):
        Task(**(fields | kwargs))


def test_duplicate_pet_names_and_task_ownership(household):
    owner, mochi, luna, _ = household
    with pytest.raises(ValueError, match="already registered"):
        owner.add_pet(Pet(" mochi ", "dog"))
    task = Task("Walk", "08:00", DAY)
    mochi.add_task(task)
    with pytest.raises(ValueError, match="already attached"):
        mochi.add_task(task)
    with pytest.raises(ValueError, match="only one pet"):
        luna.add_task(task)
