"""
Unit tests for PawPal+ core system.
Verifies Task, Pet, Owner, and Scheduler behavior.
"""

import pytest
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

