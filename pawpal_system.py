"""
PawPal+ Core System.
Defines domain entities (Task, Pet, Owner) and the central Scheduler.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from typing import List, Optional

PRIORITY_MAP = {"high": 1, "medium": 2, "low": 3}


@dataclass
class Task:
    """Represents a single pet care routine or activity."""
    title: str
    time: str  # Format: "HH:MM" in 24-hour time (e.g. "08:30")
    duration_minutes: int = 30
    frequency: str = "daily"  # "daily", "weekly", "once"
    priority: str = "medium"  # "high", "medium", "low"
    is_completed: bool = False
    pet_name: str = ""
    date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_completed = True

    def get_next_occurrence(self) -> Optional["Task"]:
        """
        Calculate and instantiate the next occurrence of a recurring task.

        Uses timedelta to advance the date based on the task's frequency:
        - "daily": advances by +1 day from the current/anchor date.
        - "weekly": advances by +7 days from the current/anchor date.
        - "once" / other: returns None (non-recurring).

        Returns:
            Optional[Task]: A new Task instance with updated due date and is_completed=False,
            or None if the task is not recurring.
        """
        freq = self.frequency.lower()
        if freq not in ("daily", "weekly"):
            return None

        days_to_add = 1 if freq == "daily" else 7
        try:
            current_dt = datetime.strptime(self.date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            current_dt = date.today()

        # Anchor to at least today so overdue tasks don't schedule new occurrences in the past
        anchor_date = max(current_dt, date.today())
        next_date = (anchor_date + timedelta(days=days_to_add)).strftime("%Y-%m-%d")

        return Task(
            title=self.title,
            time=self.time,
            duration_minutes=self.duration_minutes,
            frequency=self.frequency,
            priority=self.priority,
            is_completed=False,
            pet_name=self.pet_name,
            date=next_date,
        )


@dataclass
class Pet:
    """Stores pet details and maintains a list of assigned tasks."""
    name: str
    species: str = "dog"
    breed: str = "unknown"
    age: int = 0
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Assign a task to this pet, automatically setting pet attribution."""
        if not task.pet_name:
            task.pet_name = self.name
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return a copy of the list of tasks assigned to this pet."""
        return list(self.tasks)


@dataclass
class Owner:
    """Manages multiple pets and aggregates their care tasks."""
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's care."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Optional[Pet]:
        """Find a pet by name (case-insensitive)."""
        for p in self.pets:
            if p.name.lower() == name.lower():
                return p
        return None

    def get_all_tasks(self) -> List[Task]:
        """Retrieve every task from all pets managed by the owner."""
        all_tasks: List[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    """The planning brain that retrieves, organizes, and detects conflicts across pets."""

    def __init__(self, owner: Owner):
        """Initialize the scheduler linked to an owner instance."""
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Retrieve all tasks across all pets via Owner.get_all_tasks()."""
        return self.owner.get_all_tasks()

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """
        Mark a task complete and coordinate creating the next recurring occurrence.

        Idempotently attaches the newly generated recurring task to the appropriate
        pet in the owner's household, preventing duplicate entries for the same date.

        Args:
            task (Task): The task instance to complete.

        Returns:
            Optional[Task]: The newly created Task instance if recurring, or None.
        """
        task.mark_complete()
        next_task = task.get_next_occurrence()
        if next_task:
            pet = self.owner.get_pet(task.pet_name)
            if not pet:
                for p in self.owner.pets:
                    if p.name.lower() == task.pet_name.lower():
                        pet = p
                        break
            if pet:
                # Prevent duplicate recurrence if already present
                already_exists = any(
                    t.title == next_task.title and t.date == next_task.date
                    for t in pet.tasks
                )
                if not already_exists:
                    pet.add_task(next_task)
        return next_task

    def _parse_time(self, time_str: str) -> datetime:
        """Helper to parse a time string into a comparable datetime object."""
        cleaned = time_str.strip()
        try:
            return datetime.strptime(cleaned, "%H:%M")
        except ValueError:
            return datetime.strptime(cleaned, "%I:%M" if ":" in cleaned else "%H")

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Sort tasks chronologically by their scheduled 24-hour time string ("HH:MM").

        Parses time strings into datetime representations to ensure accurate chronological
        ordering (e.g. "08:30" < "10:00").

        Args:
            tasks (Optional[List[Task]]): List of tasks to sort. If None, sorts all tasks
                retrieved from the owner.

        Returns:
            List[Task]: A new list of tasks ordered from earliest to latest.
        """
        target_tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(target_tasks, key=lambda t: self._parse_time(t.time))

    def sort_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Sort tasks by priority weight (High -> Medium -> Low).

        Args:
            tasks (Optional[List[Task]]): List of tasks to sort. If None, sorts all tasks
                retrieved from the owner.

        Returns:
            List[Task]: A new list of tasks ordered by descending priority.
        """
        target_tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(target_tasks, key=lambda t: PRIORITY_MAP.get(t.priority.lower(), 4))

    def filter_tasks(
        self,
        pet_name: Optional[str] = None,
        is_completed: Optional[bool] = None,
        tasks: Optional[List[Task]] = None,
    ) -> List[Task]:
        """
        Filter tasks across multiple dimensions (pet name, completion status, or both).

        Performs a single-pass filter over the provided or aggregated task list.

        Args:
            pet_name (Optional[str]): Case-insensitive pet name to filter by.
            is_completed (Optional[bool]): True for completed tasks, False for pending tasks.
            tasks (Optional[List[Task]]): Task list to filter. Defaults to owner's all tasks.

        Returns:
            List[Task]: Filtered list of Task objects matching all specified criteria.
        """
        target_tasks = tasks if tasks is not None else self.get_all_tasks()
        filtered = target_tasks
        if pet_name is not None and pet_name.strip() and pet_name.lower() != "all pets":
            filtered = [t for t in filtered if t.pet_name.lower() == pet_name.strip().lower()]
        if is_completed is not None:
            filtered = [t for t in filtered if t.is_completed == is_completed]
        return filtered

    def filter_by_pet(self, pet_name: str, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Filter tasks belonging to a specific pet by name.

        Args:
            pet_name (str): The name of the pet (case-insensitive).
            tasks (Optional[List[Task]]): Optional subset of tasks to filter.

        Returns:
            List[Task]: List of tasks assigned to the specified pet.
        """
        return self.filter_tasks(pet_name=pet_name, tasks=tasks)

    def filter_by_status(self, is_completed: bool, tasks: Optional[List[Task]] = None) -> List[Task]:
        """
        Filter tasks by their completion status.

        Args:
            is_completed (bool): True for completed tasks, False for pending tasks.
            tasks (Optional[List[Task]]): Optional subset of tasks to filter.

        Returns:
            List[Task]: List of tasks matching the specified completion state.
        """
        return self.filter_tasks(is_completed=is_completed, tasks=tasks)

    def detect_conflicts(self, tasks: Optional[List[Task]] = None) -> List[str]:
        """
        Detect scheduling collisions and return actionable warning messages without crashing.

        Sorts active tasks chronologically and checks for:
        1. Exact start-time collisions (two tasks starting at the exact same minute).
        2. Interval duration overlaps (a task starting before the preceding task finishes).
        Differentiates between same-pet collisions and multi-pet household conflicts.

        Args:
            tasks (Optional[List[Task]]): Specific tasks to inspect. Defaults to the active
                daily schedule.

        Returns:
            List[str]: Formatted warning messages describing any detected collisions.
        """
        warnings: List[str] = []
        target_tasks = tasks if tasks is not None else self.get_daily_schedule()
        sorted_tasks = self.sort_by_time(target_tasks)

        for i in range(len(sorted_tasks)):
            t1 = sorted_tasks[i]
            t1_start = self._parse_time(t1.time)
            t1_end = t1_start + timedelta(minutes=t1.duration_minutes)

            for j in range(i + 1, len(sorted_tasks)):
                t2 = sorted_tasks[j]
                t2_start = self._parse_time(t2.time)

                # Since tasks are sorted chronologically, if t2 starts after or when t1 ends,
                # no subsequent task will overlap with t1
                if t2_start >= t1_end:
                    break

                is_same_pet = t1.pet_name.lower() == t2.pet_name.lower()
                scope_tag = f"Same-Pet ({t1.pet_name})" if is_same_pet else f"Multi-Pet ({t1.pet_name} & {t2.pet_name})"

                if t2_start == t1_start:
                    warnings.append(
                        f"Exact Conflict [{scope_tag}] at {t1.time}: "
                        f"'{t1.title}' and '{t2.title}' are scheduled at the exact same time."
                    )
                else:
                    warnings.append(
                        f"Overlap Conflict [{scope_tag}] at {t2.time}: "
                        f"'{t2.title}' ({t2.pet_name}) overlaps with '{t1.title}' ({t1.pet_name}, starts {t1.time}, duration {t1.duration_minutes}m)."
                    )
        return warnings

    def get_daily_schedule(self) -> List[Task]:
        """Return the prioritized and sorted daily task schedule for active tasks."""
        active_tasks = self.filter_by_status(is_completed=False)
        return self.sort_by_time(active_tasks)

    def explain_plan(self) -> List[str]:
        """Explain the daily schedule and why each task was ordered and included."""
        schedule = self.get_daily_schedule()
        if not schedule:
            return ["No pending tasks scheduled for today."]

        explanations: List[str] = []
        for task in schedule:
            reason = (
                f"[{task.time}] {task.title} for {task.pet_name} ({task.duration_minutes}m) - "
                f"Priority: {task.priority.upper()} | Frequency: {task.frequency}. "
                f"Ordered chronologically to keep {task.pet_name}'s routine consistent."
            )
            explanations.append(reason)
        return explanations

