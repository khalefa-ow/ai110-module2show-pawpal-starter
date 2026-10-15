"""PawPal+ domain model, independent of the Streamlit interface."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    """Represent one dated pet-care activity."""

    description: str
    time: str
    due_date: date = field(default_factory=date.today)
    frequency: str = "once"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this occurrence complete."""
        raise NotImplementedError


@dataclass
class Pet:
    """Store identifying details and care tasks for one pet."""

    name: str
    species: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """Manage a household's pets and aggregate their tasks."""

    name: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the household."""
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        """Collect tasks across every pet."""
        raise NotImplementedError


@dataclass
class Scheduler:
    """Organize care across all pets belonging to an owner."""

    owner: Owner

    def sort_by_time(self) -> list[Task]:
        """Return a chronological household schedule."""
        raise NotImplementedError
