"""
PawPal+ Core System Skeleton.
Defines domain entities (Task, Pet, Owner) and the central Scheduler.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """Represents a pet care task or routine."""
    title: str
    time: str  # Format: "HH:MM" in 24-hour time (e.g. "08:30")
    duration_minutes: int = 30
    frequency: str = "daily"  # "daily", "weekly", "once"
    priority: str = "medium"  # "high", "medium", "low"
    is_completed: bool = False
    pet_name: str = ""

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def get_next_occurrence(self) -> Optional["Task"]:
        """Return a new Task instance for the next occurrence if recurring."""
        pass


@dataclass
class Pet:
    """Represents a pet with associated care routines."""
    name: str
    species: str = "dog"
    breed: str = "unknown"
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet."""
        pass

    def get_tasks(self) -> List[Task]:
        """Return the list of tasks for this pet."""
        pass


@dataclass
class Owner:
    """Represents an owner who cares for one or more pets."""
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's care."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Aggregate and return every task across all pets owned."""
        pass


class Scheduler:
    """Coordinates, sorts, filters, and detects conflicts across all pet routines."""

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks from the owner's pets."""
        pass

    def sort_by_time(self) -> List[Task]:
        """Sort tasks chronologically by time."""
        pass

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Filter tasks belonging to a specific pet."""
        pass

    def filter_by_status(self, is_completed: bool) -> List[Task]:
        """Filter tasks by completion status."""
        pass

    def detect_conflicts(self) -> List[str]:
        """Identify overlapping tasks or tasks scheduled at the exact same time."""
        pass

    def get_daily_schedule(self) -> List[Task]:
        """Return the prioritized and sorted daily task schedule."""
        pass
