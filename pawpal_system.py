"""PawPal+ domain model, independent of the Streamlit interface."""

from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta
from uuid import uuid4


PRIORITIES = {"high": 0, "medium": 1, "low": 2}


def _nonempty(value: str, label: str) -> str:
    """Trim required text and reject blank values."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} is required.")
    return value.strip()


@dataclass
class Task:
    """Represent one dated pet-care activity."""

    description: str
    time: str
    due_date: date = field(default_factory=date.today)
    frequency: str = "once"
    completed: bool = False
    duration_minutes: int = 15
    priority: str = "medium"
    id: str = field(default_factory=lambda: uuid4().hex)
    pet_id: str | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Validate task details before they enter the schedule."""
        self.description = _nonempty(self.description, "Task description")
        try:
            parsed = datetime.strptime(self.time, "%H:%M")
        except (TypeError, ValueError) as exc:
            raise ValueError("Time must be a valid HH:MM value.") from exc
        if parsed.strftime("%H:%M") != self.time:
            raise ValueError("Time must use zero-padded HH:MM format.")
        if type(self.due_date) is not date:
            raise ValueError("Due date must be a date.")
        if self.frequency not in {"once", "daily", "weekly"}:
            raise ValueError("Frequency must be once, daily, or weekly.")
        if self.priority not in PRIORITIES:
            raise ValueError("Priority must be low, medium, or high.")
        if type(self.duration_minutes) is not int or self.duration_minutes <= 0:
            raise ValueError("Duration must be a positive whole number of minutes.")

    def mark_complete(self) -> None:
        """Mark this occurrence complete."""
        self.completed = True


@dataclass
class Pet:
    """Store identifying details and care tasks for one pet."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)
    breed: str = ""
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        """Validate pet details and attach any initial tasks."""
        self.name = _nonempty(self.name, "Pet name")
        self.species = _nonempty(self.species, "Species")
        initial_tasks, self.tasks = self.tasks, []
        for task in initial_tasks:
            self.add_task(task)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        if task.pet_id is not None and task.pet_id != self.id:
            raise ValueError("A task can belong to only one pet.")
        if any(existing.id == task.id for existing in self.tasks):
            raise ValueError("This task is already attached to the pet.")
        task.pet_id = self.id
        self.tasks.append(task)

    def list_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def update_task(self, task_id: str, **changes) -> Task:
        """Validate and replace the editable details of a pending task."""
        allowed = {
            "description",
            "time",
            "due_date",
            "frequency",
            "duration_minutes",
            "priority",
        }
        if set(changes) - allowed:
            raise ValueError("Only scheduling details can be edited.")
        for index, task in enumerate(self.tasks):
            if task.id == task_id:
                if task.completed:
                    raise ValueError("Completed occurrences cannot be edited.")
                updated = replace(task, **changes)
                updated.pet_id = self.id
                self.tasks[index] = updated
                return updated
        raise ValueError("Task not found for this pet.")


@dataclass
class Owner:
    """Manage a household's pets and aggregate their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate the owner and register any initial pets."""
        self.name = _nonempty(self.name, "Owner name")
        initial_pets, self.pets = self.pets, []
        for pet in initial_pets:
            self.add_pet(pet)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the household."""
        if any(
            p.id == pet.id or p.name.casefold() == pet.name.casefold()
            for p in self.pets
        ):
            raise ValueError("A pet with that name is already registered.")
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks across every pet."""
        return [task for pet in self.pets for task in pet.list_tasks()]

    def get_pet(self, pet_id: str) -> Pet:
        """Look up a registered pet by stable identifier."""
        for pet in self.pets:
            if pet.id == pet_id:
                return pet
        raise ValueError("Pet not found.")


@dataclass
class Scheduler:
    """Organize care across all pets belonging to an owner."""

    owner: Owner

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Return a chronological household schedule."""
        source = self.owner.get_all_tasks() if tasks is None else tasks
        return sorted(source, key=lambda task: (task.due_date, task.time))

    def filter_tasks(
        self,
        pet_name: str | None = None,
        completed: bool | None = None,
        on_date: date | None = None,
    ) -> list[Task]:
        """Filter household tasks by pet, completion status, and/or exact date."""
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            pet_ids = {
                p.id
                for p in self.owner.pets
                if p.name.casefold() == pet_name.casefold()
            }
            tasks = [task for task in tasks if task.pet_id in pet_ids]
        if completed is not None:
            tasks = [task for task in tasks if task.completed == completed]
        if on_date is not None:
            tasks = [task for task in tasks if task.due_date == on_date]
        return self.sort_by_time(tasks)

    def sort_by_priority(self, tasks: list[Task] | None = None) -> list[Task]:
        """Rank high priority first, breaking ties by date and time."""
        source = self.owner.get_all_tasks() if tasks is None else tasks
        return sorted(
            source,
            key=lambda task: (PRIORITIES[task.priority], task.due_date, task.time),
        )

    def mark_task_complete(
        self, task_id: str, completed_on: date | None = None
    ) -> Task | None:
        """Complete once and attach a fresh next occurrence for recurring tasks."""
        task = next((t for t in self.owner.get_all_tasks() if t.id == task_id), None)
        if task is None:
            raise ValueError("Task not found.")
        if task.completed:
            return None
        next_task = None
        if task.frequency != "once":
            days = 1 if task.frequency == "daily" else 7
            next_date = max(task.due_date, completed_on or date.today()) + timedelta(
                days=days
            )
            next_task = replace(
                task, due_date=next_date, completed=False, id=uuid4().hex
            )
            self.owner.get_pet(task.pet_id).add_task(next_task)
        task.mark_complete()
        return next_task

    def detect_conflicts(self, on_date: date | None = None) -> list[str]:
        """Warn about pending tasks sharing an exact date and start time."""
        slots: dict[tuple[date, str], list[Task]] = {}
        for task in self.filter_tasks(completed=False, on_date=on_date):
            slots.setdefault((task.due_date, task.time), []).append(task)
        warnings = []
        for (day, time), tasks in slots.items():
            if len(tasks) > 1:
                labels = [
                    f"{self.owner.get_pet(t.pet_id).name}: {t.description}"
                    for t in tasks
                ]
                warnings.append(
                    f"{day.isoformat()} {time} - Conflict: " + "; ".join(labels)
                )
        return warnings

    def build_plan(
        self, on_date: date, available_minutes: int
    ) -> tuple[list[Task], list[str]]:
        """Greedily select pending tasks by priority within a time budget and without overlaps."""
        if type(available_minutes) is not int or available_minutes < 0:
            raise ValueError(
                "Time budget must be a nonnegative whole number of minutes."
            )
        chosen: list[Task] = []
        skipped: list[str] = []
        intervals: list[tuple[datetime, datetime]] = []
        remaining = available_minutes
        candidates = self.sort_by_priority(
            self.filter_tasks(completed=False, on_date=on_date)
        )
        for task in candidates:
            label = f"{self.owner.get_pet(task.pet_id).name}: {task.description}"
            start = datetime.combine(
                task.due_date, datetime.strptime(task.time, "%H:%M").time()
            )
            end = start + timedelta(minutes=task.duration_minutes)
            if task.duration_minutes > remaining:
                skipped.append(
                    f"{label} - exceeds the remaining {remaining} minute budget."
                )
            elif any(
                start < other_end and other_start < end
                for other_start, other_end in intervals
            ):
                skipped.append(f"{label} - overlaps a higher-ranked task.")
            else:
                chosen.append(task)
                intervals.append((start, end))
                remaining -= task.duration_minutes
        return self.sort_by_time(chosen), skipped
