"""
PawPal+ Core System.
Defines domain entities (Task, Pet, Owner) and the central Scheduler.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
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
        """Return a new Task instance for the next occurrence if this task is recurring."""
        freq = self.frequency.lower()
        if freq not in ("daily", "weekly"):
            return None

        days_to_add = 1 if freq == "daily" else 7
        try:
            current_dt = datetime.strptime(self.date, "%Y-%m-%d")
        except (ValueError, TypeError):
            current_dt = datetime.now()

        next_date = (current_dt + timedelta(days=days_to_add)).strftime("%Y-%m-%d")

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
        """Mark a task complete and automatically attach the next recurring task to the pet."""
        task.mark_complete()
        next_task = task.get_next_occurrence()
        if next_task:
            pet = self.owner.get_pet(task.pet_name)
            if pet:
                pet.add_task(next_task)
            else:
                for p in self.owner.pets:
                    if p.name.lower() == task.pet_name.lower():
                        p.add_task(next_task)
                        break
        return next_task

    def _parse_time(self, time_str: str) -> datetime:
        """Helper to parse a time string into a comparable datetime object."""
        cleaned = time_str.strip()
        try:
            return datetime.strptime(cleaned, "%H:%M")
        except ValueError:
            return datetime.strptime(cleaned, "%I:%M" if ":" in cleaned else "%H")

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks chronologically by their scheduled time."""
        target_tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(target_tasks, key=lambda t: self._parse_time(t.time))

    def sort_by_priority(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Sort tasks by priority weight (high first, then medium, then low)."""
        target_tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(target_tasks, key=lambda t: PRIORITY_MAP.get(t.priority.lower(), 4))

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Filter tasks belonging to a specific pet."""
        return [t for t in self.get_all_tasks() if t.pet_name.lower() == pet_name.lower()]

    def filter_by_status(self, is_completed: bool) -> List[Task]:
        """Filter tasks by completion status."""
        return [t for t in self.get_all_tasks() if t.is_completed == is_completed]

    def detect_conflicts(self) -> List[str]:
        """Identify overlapping tasks or tasks scheduled at the exact same time."""
        warnings: List[str] = []
        tasks = self.sort_by_time()

        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                t1, t2 = tasks[i], tasks[j]
                t1_start = self._parse_time(t1.time)
                t1_end = t1_start + timedelta(minutes=t1.duration_minutes)
                t2_start = self._parse_time(t2.time)

                if t2_start == t1_start:
                    warnings.append(
                        f"Exact time conflict at {t1.time}: '{t1.title}' ({t1.pet_name}) and '{t2.title}' ({t2.pet_name}) are scheduled at the same time."
                    )
                elif t2_start < t1_end:
                    warnings.append(
                        f"Overlap conflict at {t2.time}: '{t2.title}' ({t2.pet_name}) overlaps with '{t1.title}' ({t1.pet_name}, starts {t1.time}, duration {t1.duration_minutes}m)."
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

