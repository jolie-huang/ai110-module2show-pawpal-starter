"""
Unit tests for PawPal+ core system.
Verifies Task, Pet, Owner, and Scheduler behavior across:
- Sorting Correctness (chronological ordering, single-digit vs double-digit hours)
- Recurrence Logic (daily/weekly rollovers, one-time tasks, idempotency, date anchoring)
- Conflict Detection (exact duplicate start times, duration overlaps, back-to-back non-conflicts)
- Entity Management & Filtering (automatic attribution, multi-pet aggregation, empty states)
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ==============================================================================
# 1. SORTING CORRECTNESS TESTS
# ==============================================================================

def test_sorting_by_time_chronological():
    """Verify that tasks added out of order are sorted in strict chronological order."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    t1 = Task(title="Evening Dinner", time="18:00")
    t2 = Task(title="Morning Breakfast", time="08:30")
    t3 = Task(title="Midday Walk", time="12:00")

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_by_time()

    assert [t.time for t in sorted_tasks] == ["08:30", "12:00", "18:00"]
    assert [t.title for t in sorted_tasks] == [
        "Morning Breakfast",
        "Midday Walk",
        "Evening Dinner",
    ]


def test_sorting_handles_single_digit_and_boundary_hours():
    """
    Verify that single-digit hours ("8:00") sort before double-digit hours ("10:00").
    Plain string comparison fails this test because "1" < "8", but datetime parsing succeeds.
    """
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    t1 = Task(title="Late Morning Walk", time="10:00")
    t2 = Task(title="Early Morning Potty", time="8:00")
    t3 = Task(title="Midnight Check", time="00:15")
    t4 = Task(title="Late Night Wind-down", time="23:45")

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)
    pet.add_task(t4)

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_by_time()

    assert [t.title for t in sorted_tasks] == [
        "Midnight Check",
        "Early Morning Potty",
        "Late Morning Walk",
        "Late Night Wind-down",
    ]


def test_sorting_by_priority():
    """Verify tasks are sorted descending by priority: High (1) -> Medium (2) -> Low (3)."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    pet.add_task(Task(title="Brush Coat", time="14:00", priority="low"))
    pet.add_task(Task(title="Give Insulin Meds", time="09:00", priority="high"))
    pet.add_task(Task(title="Lunch Treat", time="12:00", priority="medium"))

    scheduler = Scheduler(owner=owner)
    sorted_by_prio = scheduler.sort_by_priority()

    assert [t.priority for t in sorted_by_prio] == ["high", "medium", "low"]


# ==============================================================================
# 2. RECURRENCE LOGIC TESTS
# ==============================================================================

def test_daily_recurrence_creates_next_day_task():
    """
    Verify that completing a daily task creates the next occurrence for tomorrow,
    resets completion status to False, and attaches to the appropriate pet.
    """
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    daily_task = Task(
        title="Morning Walk",
        time="08:00",
        duration_minutes=30,
        frequency="daily",
        priority="high",
    )
    pet.add_task(daily_task)

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.mark_task_complete(daily_task)

    # 1. Original task is marked completed
    assert daily_task.is_completed is True

    # 2. Next task instance is created with correct properties
    assert next_task is not None
    assert next_task.title == "Morning Walk"
    assert next_task.time == "08:00"
    assert next_task.priority == "high"
    assert next_task.frequency == "daily"
    assert next_task.is_completed is False
    assert next_task.pet_name == "Mochi"

    # 3. Next date is exactly tomorrow
    expected_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    assert next_task.date == expected_date

    # 4. Pet's task list now contains both the completed original and the upcoming task
    assert len(pet.get_tasks()) == 2
    assert pet.get_tasks()[1] == next_task


def test_weekly_recurrence_creates_seven_days_later():
    """Verify that completing a weekly task creates the next occurrence 7 days later."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Luna")
    owner.add_pet(pet)

    weekly_task = Task(title="Brush Coat", time="14:00", frequency="weekly")
    pet.add_task(weekly_task)

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.mark_task_complete(weekly_task)

    assert weekly_task.is_completed is True
    assert next_task is not None
    assert next_task.is_completed is False
    expected_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    assert next_task.date == expected_date
    assert len(pet.get_tasks()) == 2


def test_one_time_task_does_not_recur():
    """Verify that completing a one-time ("once") task does not create a recurring instance."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Luna")
    owner.add_pet(pet)

    once_task = Task(title="Annual Vet Checkup", time="09:00", frequency="once")
    pet.add_task(once_task)

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.mark_task_complete(once_task)

    assert once_task.is_completed is True
    assert next_task is None
    assert len(pet.get_tasks()) == 1


def test_recurrence_overdue_task_anchored_to_today():
    """Verify overdue recurring tasks anchor rollover to today so new occurrences are not in the past."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    overdue_task = Task(title="Old Walk", time="08:00", frequency="daily", date="2020-01-01")
    pet.add_task(overdue_task)

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.mark_task_complete(overdue_task)

    assert next_task is not None
    expected_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    assert next_task.date == expected_date


def test_recurrence_idempotency_prevents_duplicate_entries():
    """Verify calling mark_task_complete repeatedly does not inject duplicate tasks for the same date."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    task = Task(title="Evening Potty", time="21:00", frequency="daily")
    pet.add_task(task)

    scheduler = Scheduler(owner=owner)
    scheduler.mark_task_complete(task)
    assert len(pet.get_tasks()) == 2

    # Calling completion again should not add a duplicate recurrence
    scheduler.mark_task_complete(task)
    assert len(pet.get_tasks()) == 2


# ==============================================================================
# 3. CONFLICT DETECTION TESTS
# ==============================================================================

def test_conflict_detection_flags_exact_duplicate_times_same_pet():
    """Verify that Scheduler flags exact duplicate start times for the same pet."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    pet.add_task(Task(title="Breakfast", time="08:30", duration_minutes=15))
    pet.add_task(Task(title="Morning Medication", time="08:30", duration_minutes=10))

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Exact Conflict" in conflicts[0]
    assert "Same-Pet (Mochi)" in conflicts[0]
    assert "08:30" in conflicts[0]


def test_conflict_detection_flags_exact_duplicate_times_different_pets():
    """Verify that Scheduler flags exact duplicate start times across different pets."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi")
    cat = Pet(name="Luna")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(title="Dog Walk", time="09:00", duration_minutes=30))
    cat.add_task(Task(title="Cat Feeding", time="09:00", duration_minutes=15))

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Exact Conflict" in conflicts[0]
    assert "Multi-Pet" in conflicts[0]
    assert "09:00" in conflicts[0]


def test_conflict_detection_duration_overlap():
    """Verify that Scheduler flags a task starting before the previous task finishes."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    # Task 1: 08:00 -> 08:30 (30 minutes)
    pet.add_task(Task(title="Bath", time="08:00", duration_minutes=30))
    # Task 2 starts at 08:20, which is before 08:30
    pet.add_task(Task(title="Nail Trim", time="08:20", duration_minutes=15))

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Overlap Conflict" in conflicts[0]
    assert "08:20" in conflicts[0]


def test_back_to_back_tasks_do_not_conflict():
    """Verify that a task starting at the exact moment the previous task finishes is NOT a conflict."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    # Task 1: 08:00 to 08:30 (30m)
    pet.add_task(Task(title="Morning Walk", time="08:00", duration_minutes=30))
    # Task 2: 08:30 to 08:45 (starts exactly when Task 1 ends)
    pet.add_task(Task(title="Breakfast", time="08:30", duration_minutes=15))

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 0


def test_completed_tasks_do_not_trigger_daily_conflicts():
    """Verify that completed tasks do not trigger conflicts against active pending tasks."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    completed_task = Task(title="Early Walk", time="08:00", duration_minutes=30, is_completed=True)
    pending_task = Task(title="Alternate Vet Call", time="08:00", duration_minutes=30, is_completed=False)

    pet.add_task(completed_task)
    pet.add_task(pending_task)

    scheduler = Scheduler(owner=owner)
    # Default detect_conflicts inspects get_daily_schedule() (active pending tasks only)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0


# ==============================================================================
# 4. ENTITY MANAGEMENT & FILTERING TESTS
# ==============================================================================

def test_task_mark_complete():
    """Verify that mark_complete() changes is_completed to True."""
    task = Task(title="Play Time", time="15:00")
    assert task.is_completed is False

    task.mark_complete()
    assert task.is_completed is True


def test_pet_task_addition_and_attribution():
    """Verify that adding a task to a Pet stamps the pet's name onto the task."""
    pet = Pet(name="Mochi", species="Dog")
    assert len(pet.get_tasks()) == 0

    task = Task(title="Park Trip", time="16:00")
    pet.add_task(task)

    assert len(pet.get_tasks()) == 1
    assert task.pet_name == "Mochi"


def test_owner_multi_pet_aggregation():
    """Verify that Owner.get_all_tasks() aggregates tasks across all owned pets."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi")
    cat = Pet(name="Luna")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(title="Walk Dog", time="08:00"))
    cat.add_task(Task(title="Feed Cat", time="08:30"))

    scheduler = Scheduler(owner=owner)
    all_tasks = scheduler.get_all_tasks()

    assert len(all_tasks) == 2
    assert {t.pet_name for t in all_tasks} == {"Mochi", "Luna"}


def test_filtering_by_pet_and_status():
    """Verify filtering tasks by pet name, completion status, and combined criteria."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi")
    cat = Pet(name="Luna")
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task(title="Walk Dog", time="08:00", is_completed=True))
    dog.add_task(Task(title="Feed Dog", time="09:00", is_completed=False))
    cat.add_task(Task(title="Brush Cat", time="10:00", is_completed=False))

    scheduler = Scheduler(owner=owner)

    # Filter by pet
    assert len(scheduler.filter_tasks(pet_name="Mochi")) == 2
    assert len(scheduler.filter_tasks(pet_name="Luna")) == 1

    # Filter by completion status
    assert len(scheduler.filter_tasks(is_completed=True)) == 1
    assert len(scheduler.filter_tasks(is_completed=False)) == 2

    # Combined filter
    pending_dog_tasks = scheduler.filter_tasks(pet_name="Mochi", is_completed=False)
    assert len(pending_dog_tasks) == 1
    assert pending_dog_tasks[0].title == "Feed Dog"


def test_empty_states_handled_gracefully():
    """Verify that empty pet lists, task lists, and plan explanations execute without errors."""
    empty_owner = Owner(name="Sam")
    scheduler = Scheduler(owner=empty_owner)

    assert scheduler.get_all_tasks() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.explain_plan() == ["No pending tasks scheduled for today."]

    # Pet with no tasks
    empty_owner.add_pet(Pet(name="NewPet"))
    assert scheduler.get_all_tasks() == []
    assert scheduler.filter_tasks(pet_name="NewPet") == []
