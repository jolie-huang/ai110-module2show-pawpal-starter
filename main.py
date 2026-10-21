"""
PawPal+ CLI Demo Script.
Demonstrates multi-pet task management, chronological scheduling, and conflict detection.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_banner(title: str) -> None:
    print(f"\n{'=' * 60}\n🐾 {title.upper()}\n{'=' * 60}")


def main() -> None:
    print_banner("PawPal+ Pet Care Management Demo")

    # 1. Create an Owner
    owner = Owner(name="Jordan")
    print(f"👤 Owner: {owner.name}")

    # 2. Create at least two Pets
    mochi = Pet(name="Mochi", species="Dog", breed="Golden Retriever", age=3)
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=2)

    owner.add_pet(mochi)
    owner.add_pet(luna)
    print(f"🐶 Added Pet: {mochi.name} ({mochi.breed}, {mochi.age} yrs)")
    print(f"🐱 Added Pet: {luna.name} ({luna.breed}, {luna.age} yrs)")

    # 3. Add at least three Tasks with different times across pets
    t1 = Task(
        title="Morning Walk & Potty",
        time="08:00",
        duration_minutes=30,
        priority="high",
        frequency="daily"
    )
    t2 = Task(
        title="Breakfast & Supplements",
        time="08:45",
        duration_minutes=15,
        priority="high",
        frequency="daily"
    )
    t3 = Task(
        title="Brush Coat & Grooming",
        time="14:00",
        duration_minutes=20,
        priority="medium",
        frequency="weekly"
    )
    t4 = Task(
        title="Catnip Play Session",
        time="09:15",
        duration_minutes=25,
        priority="medium",
        frequency="daily"
    )
    # Add a conflicting task to test conflict detection
    t5 = Task(
        title="Vet Video Checkup",
        time="08:45",
        duration_minutes=30,
        priority="high",
        frequency="once"
    )

    mochi.add_task(t1)
    mochi.add_task(t2)
    mochi.add_task(t3)
    luna.add_task(t4)
    luna.add_task(t5)

    # 4. Initialize the Scheduler
    scheduler = Scheduler(owner=owner)

    # 5. Print Today's Schedule
    print_banner("Today's Schedule (Chronological)")
    daily_schedule = scheduler.get_daily_schedule()

    print(f"{'Time':<8} | {'Pet':<8} | {'Task':<26} | {'Dur':<6} | {'Priority':<8} | {'Status'}")
    print(f"{'-' * 8}-+-{'-' * 8}-+-{'-' * 26}-+-{'-' * 6}-+-{'-' * 8}-+-{'-' * 10}")
    for task in daily_schedule:
        status = "Completed" if task.is_completed else "Pending"
        print(
            f"{task.time:<8} | {task.pet_name:<8} | {task.title:<26} | "
            f"{str(task.duration_minutes) + 'm':<6} | {task.priority.capitalize():<8} | {status}"
        )

    # 6. Check for Task Conflicts
    print_banner("Smart Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"⚠️  {warning}")
    else:
        print("✅ No schedule conflicts detected.")

    # 7. Plan Explanations
    print_banner("Plan Reasoning & Explanations")
    for explanation in scheduler.explain_plan():
        print(f"• {explanation}")

    # 8. Mark a Task Complete and verify Recurring creation
    print_banner("Recurring Task Verification")
    print(f"Marking '{t1.title}' complete...")
    new_task = scheduler.mark_task_complete(t1)
    print(f"Status of original task: is_completed = {t1.is_completed}")
    if new_task:
        print(f"✅ Recurring task auto-generated for {new_task.pet_name}: '{new_task.title}' on {new_task.date} at {new_task.time}")


if __name__ == "__main__":
    main()

