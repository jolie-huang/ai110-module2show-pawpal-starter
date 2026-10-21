"""
PawPal+ CLI Demo Script.
Demonstrates multi-pet task management, out-of-order task addition,
chronological sorting, filtering (by pet and status), and lightweight conflict detection.
"""

from pawpal_system import Owner, Pet, Task, Scheduler


def print_banner(title: str) -> None:
    print(f"\n{'=' * 60}\n🐾 {title.upper()}\n{'=' * 60}")


def print_task_table(tasks, title: str) -> None:
    print_banner(title)
    print(f"{'Time':<8} | {'Pet':<8} | {'Task':<26} | {'Dur':<6} | {'Priority':<8} | {'Status'}")
    print(f"{'-' * 8}-+-{'-' * 8}-+-{'-' * 26}-+-{'-' * 6}-+-{'-' * 8}-+-{'-' * 10}")
    for task in tasks:
        status = "Completed" if task.is_completed else "Pending"
        print(
            f"{task.time:<8} | {task.pet_name:<8} | {task.title:<26} | "
            f"{str(task.duration_minutes) + 'm':<6} | {task.priority.capitalize():<8} | {status}"
        )


def main() -> None:
    print_banner("PawPal+ Pet Care Management Demo")

    # 1. Create an Owner
    owner = Owner(name="Jordan")
    print(f"👤 Owner: {owner.name}")

    # 2. Create Pets
    mochi = Pet(name="Mochi", species="Dog", breed="Golden Retriever", age=3)
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=2)

    owner.add_pet(mochi)
    owner.add_pet(luna)
    print(f"🐶 Added Pet: {mochi.name} ({mochi.breed}, {mochi.age} yrs)")
    print(f"🐱 Added Pet: {luna.name} ({luna.breed}, {luna.age} yrs)")

    # 3. Add Tasks deliberately OUT OF CHRONOLOGICAL ORDER across pets
    # Includes both Same-Pet and Multi-Pet same-time collisions to test conflict detection
    t_afternoon = Task(
        title="Brush Coat & Grooming",
        time="14:00",
        duration_minutes=20,
        priority="medium",
        frequency="weekly"
    )
    t_evening = Task(
        title="Evening Walk & Wind-down",
        time="19:30",
        duration_minutes=25,
        priority="medium",
        frequency="daily"
    )
    t_morning_walk = Task(
        title="Morning Walk & Potty",
        time="08:00",
        duration_minutes=30,
        priority="high",
        frequency="daily"
    )
    t_breakfast = Task(
        title="Breakfast & Supplements",
        time="08:45",
        duration_minutes=15,
        priority="high",
        frequency="daily"
    )
    # Same-pet collision for Mochi: Scheduled at 08:45 (same as Breakfast)
    t_mochi_meds = Task(
        title="Flea & Tick Prevention",
        time="08:45",
        duration_minutes=10,
        priority="high",
        frequency="monthly"
    )
    t_catnip = Task(
        title="Catnip Play Session",
        time="09:15",
        duration_minutes=25,
        priority="medium",
        frequency="daily"
    )
    # Multi-pet collision: Luna's vet checkup also scheduled at 08:45
    t_vet = Task(
        title="Vet Video Checkup",
        time="08:45",
        duration_minutes=30,
        priority="high",
        frequency="once"
    )

    # Adding tasks out of order
    mochi.add_task(t_afternoon)
    mochi.add_task(t_evening)
    mochi.add_task(t_morning_walk)
    mochi.add_task(t_breakfast)
    mochi.add_task(t_mochi_meds)
    luna.add_task(t_catnip)
    luna.add_task(t_vet)

    # 4. Initialize the Scheduler
    scheduler = Scheduler(owner=owner)

    # 5. Show Raw Out-of-Order Tasks vs. Chronologically Sorted Schedule
    print_task_table(scheduler.get_all_tasks(), "1. Raw Tasks as Added (Out of Order)")

    sorted_tasks = scheduler.sort_by_time()
    print_task_table(sorted_tasks, "2. Chronologically Sorted Schedule")

    # 6. Test Filtering by Pet Name
    mochi_tasks = scheduler.filter_tasks(pet_name="Mochi")
    print_task_table(mochi_tasks, "3. Filter by Pet: Mochi's Tasks Only")

    luna_tasks = scheduler.filter_tasks(pet_name="Luna")
    print_task_table(luna_tasks, "4. Filter by Pet: Luna's Tasks Only")

    # 7. Check for Task Conflicts (Lightweight Warnings)
    print_banner("5. Lightweight Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print(f"Detected {len(conflicts)} conflict(s) (non-blocking warnings):")
        for warning in conflicts:
            print(f"  ⚠️  {warning}")
    else:
        print("✅ No schedule conflicts detected.")

    # 8. Plan Explanations
    print_banner("6. Plan Reasoning & Explanations")
    for explanation in scheduler.explain_plan():
        print(f"• {explanation}")

    # 9. Test Status Filtering & Recurring Task Lifecycle
    print_banner("7. Task Completion & Status Filtering")
    print(f"Marking '{t_morning_walk.title}' as completed...")
    new_task = scheduler.mark_task_complete(t_morning_walk)
    if new_task:
        print(f"✅ Recurring task auto-generated for {new_task.pet_name}: '{new_task.title}' on {new_task.date} at {new_task.time}")

    completed_tasks = scheduler.filter_tasks(is_completed=True)
    print_task_table(completed_tasks, "Completed Tasks (filter_tasks: is_completed=True)")

    pending_tasks = scheduler.filter_tasks(is_completed=False)
    print_task_table(pending_tasks, "Pending Tasks (filter_tasks: is_completed=False)")


if __name__ == "__main__":
    main()
