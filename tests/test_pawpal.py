"""
Unit tests for PawPal+ core system.
Verifies Task, Pet, Owner, and Scheduler behavior.
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_completion():
    """Verify that calling mark_complete() actually changes the task's status."""
    task = Task(title="Morning Walk", time="08:00")
    assert task.is_completed is False

    task.mark_complete()
    assert task.is_completed is True


def test_task_addition():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Mochi", species="Dog")
    assert len(pet.get_tasks()) == 0

    task1 = Task(title="Morning Walk", time="08:00")
    pet.add_task(task1)
    assert len(pet.get_tasks()) == 1
    assert pet.get_tasks()[0].title == "Morning Walk"
    assert task1.pet_name == "Mochi"

    task2 = Task(title="Dinner", time="18:00")
    pet.add_task(task2)
    assert len(pet.get_tasks()) == 2


def test_sorting_by_time():
    """Verify that tasks added out of order are sorted chronologically."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    t1 = Task(title="Dinner", time="18:00")
    t2 = Task(title="Breakfast", time="08:30")
    t3 = Task(title="Noon Walk", time="12:00")

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    scheduler = Scheduler(owner=owner)
    sorted_tasks = scheduler.sort_by_time()

    assert [t.time for t in sorted_tasks] == ["08:30", "12:00", "18:00"]


def test_filtering_by_pet_and_status():
    """Verify filtering by pet name, status, and both."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi")
    cat = Pet(name="Luna")
    owner.add_pet(dog)
    owner.add_pet(cat)

    t1 = Task(title="Walk Dog", time="08:00", is_completed=True)
    t2 = Task(title="Feed Dog", time="09:00", is_completed=False)
    t3 = Task(title="Brush Cat", time="10:00", is_completed=False)

    dog.add_task(t1)
    dog.add_task(t2)
    cat.add_task(t3)

    scheduler = Scheduler(owner=owner)

    # Filter by pet
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    assert len(mochi_tasks) == 2

    luna_tasks = scheduler.filter_tasks(pet_name="Luna")
    assert len(luna_tasks) == 1
    assert luna_tasks[0].title == "Brush Cat"

    # Filter by status
    completed = scheduler.filter_tasks(is_completed=True)
    assert len(completed) == 1
    assert completed[0].title == "Walk Dog"

    pending = scheduler.filter_tasks(is_completed=False)
    assert len(pending) == 2

    # Combined filter
    mochi_pending = scheduler.filter_tasks(pet_name="Mochi", is_completed=False)
    assert len(mochi_pending) == 1
    assert mochi_pending[0].title == "Feed Dog"


def test_daily_recurring_task_creation():
    """Verify that completing a daily task creates the next occurrence for tomorrow."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi")
    owner.add_pet(pet)

    daily_task = Task(title="Morning Walk", time="08:00", frequency="daily")
    pet.add_task(daily_task)

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.mark_task_complete(daily_task)

    assert daily_task.is_completed is True
    assert next_task is not None
    assert next_task.title == "Morning Walk"
    assert next_task.is_completed is False
    assert next_task.pet_name == "Mochi"
    expected_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    assert next_task.date == expected_date
    assert len(pet.get_tasks()) == 2


def test_weekly_recurring_task_creation():
    """Verify that completing a weekly task creates the next occurrence for 7 days later."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Luna")
    owner.add_pet(pet)

    weekly_task = Task(title="Brush Coat", time="14:00", frequency="weekly")
    pet.add_task(weekly_task)

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.mark_task_complete(weekly_task)

    assert weekly_task.is_completed is True
    assert next_task is not None
    expected_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    assert next_task.date == expected_date
    assert len(pet.get_tasks()) == 2


def test_one_time_task_does_not_recur():
    """Verify that one-time tasks do not generate a recurring instance."""
    owner = Owner(name="Jordan")
    pet = Pet(name="Luna")
    owner.add_pet(pet)

    once_task = Task(title="Vet Checkup", time="09:00", frequency="once")
    pet.add_task(once_task)

    scheduler = Scheduler(owner=owner)
    next_task = scheduler.mark_task_complete(once_task)

    assert once_task.is_completed is True
    assert next_task is None
    assert len(pet.get_tasks()) == 1


def test_conflict_detection_same_and_different_pets():
    """Verify that detect_conflicts finds same-pet and multi-pet clashes without errors."""
    owner = Owner(name="Jordan")
    dog = Pet(name="Mochi")
    cat = Pet(name="Luna")
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Same pet same time
    dog.add_task(Task(title="Breakfast", time="08:30", duration_minutes=15))
    dog.add_task(Task(title="Meds", time="08:30", duration_minutes=10))

    # Different pet same time
    cat.add_task(Task(title="Vet Call", time="08:30", duration_minutes=30))

    # Overlapping task
    dog.add_task(Task(title="Walk", time="08:40", duration_minutes=30))

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) > 0
    assert any("Same-Pet" in c for c in conflicts)
    assert any("Multi-Pet" in c for c in conflicts)
