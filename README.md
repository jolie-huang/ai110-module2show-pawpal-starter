# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🏗️ Implementation Summary

PawPal+ is built as a modular, object-oriented system in pawpal_system.py. There are four main classes:

Task is a dataclass that represents one care activity, like a feeding, a walk, or giving medication. It holds the title, scheduled time (as "HH:MM"), duration, priority (high, medium, or low), frequency (daily, weekly, or once), whether it's been completed, and which pet it belongs to. It also figures out its own next occurrence date using get_next_occurrence() and timedelta.

Pet is also a dataclass. It stores the pet's identity (name, species, breed, age) and keeps its own private list of tasks. When you call add_task(), it automatically stamps the pet's name onto the task so the attribution doesn't get lost.

Owner is a dataclass for the person caring for the pets. It has add_pet() and get_all_tasks(), and the latter goes through every pet and pulls their tasks into one combined list without exposing how things are stored internally.

Scheduler is the central coordinator and the brain of the whole thing. It takes an Owner and only talks to it through Owner.get_all_tasks(), which is what makes the multi-pet support work. From there it handles sorting by time, ordering by priority, filtering by status or pet, detecting overlaps and exact conflicts, explaining the plan, and managing the lifecycle of recurring tasks.

### How the Classes Work Together

```text
[Owner] 1 ──── * [Pet] 1 ──── * [Task]
   ▲
   │ (queries via get_all_tasks())
[Scheduler] ─── (Sorts, Filters, Detects Conflicts, Explains Plan)
```

1. **Task Attribution**: When an `Owner` adds tasks to a `Pet`, the `Pet` ensures each `Task` carries its `pet_name`.
2. **Multi-Pet Retrieval**: The `Scheduler` queries `Owner.get_all_tasks()`, collecting tasks across all pets seamlessly.
3. **Smart Coordination**: The `Scheduler` sorts the master routine chronologically, detects overlapping conflicts, and when a task is completed, coordinates re-attaching the next recurring task to the correct pet.

## 🖥️ Sample Output

Sample terminal output from running the CLI demo (`python main.py`):

```text
============================================================
🐾 PAWPAL+ PET CARE MANAGEMENT DEMO
============================================================
👤 Owner: Jordan
🐶 Added Pet: Mochi (Golden Retriever, 3 yrs)
🐱 Added Pet: Luna (Siamese, 2 yrs)

============================================================
🐾 TODAY'S SCHEDULE (CHRONOLOGICAL)
============================================================
Time     | Pet      | Task                       | Dur    | Priority | Status
---------+----------+----------------------------+--------+----------+-----------
08:00    | Mochi    | Morning Walk & Potty       | 30m    | High     | Pending
08:45    | Mochi    | Breakfast & Supplements    | 15m    | High     | Pending
08:45    | Luna     | Vet Video Checkup          | 30m    | High     | Pending
09:15    | Luna     | Catnip Play Session        | 25m    | Medium   | Pending
14:00    | Mochi    | Brush Coat & Grooming      | 20m    | Medium   | Pending

============================================================
🐾 SMART CONFLICT DETECTION
============================================================
⚠️  Exact time conflict at 08:45: 'Breakfast & Supplements' (Mochi) and 'Vet Video Checkup' (Luna) are scheduled at the same time.

============================================================
🐾 PLAN REASONING & EXPLANATIONS
============================================================
• [08:00] Morning Walk & Potty for Mochi (30m) - Priority: HIGH | Frequency: daily. Ordered chronologically to keep Mochi's routine consistent.
• [08:45] Breakfast & Supplements for Mochi (15m) - Priority: HIGH | Frequency: daily. Ordered chronologically to keep Mochi's routine consistent.
• [08:45] Vet Video Checkup for Luna (30m) - Priority: HIGH | Frequency: once. Ordered chronologically to keep Luna's routine consistent.
• [09:15] Catnip Play Session for Luna (25m) - Priority: MEDIUM | Frequency: daily. Ordered chronologically to keep Luna's routine consistent.
• [14:00] Brush Coat & Grooming for Mochi (20m) - Priority: MEDIUM | Frequency: weekly. Ordered chronologically to keep Mochi's routine consistent.

============================================================
🐾 RECURRING TASK VERIFICATION
============================================================
Marking 'Morning Walk & Potty' complete...
Status of original task: is_completed = True
✅ Recurring task auto-generated for Mochi: 'Morning Walk & Potty' on 2026-10-22 at 08:00
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```text
============================= test session starts =============================
platform win32 -- Python 3.15.0, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\jolie\Downloads\codepath\ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collecting ... collected 2 items

tests/test_pawpal.py::test_task_completion PASSED                        [ 50%]
tests/test_pawpal.py::test_task_addition PASSED                          [100%]

============================== 2 passed in 0.04s ==============================
```

**Confidence Level**: ⭐⭐⭐⭐⭐ (5/5 stars)

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Sorts chronologically by 24h time or by priority weight |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Filters tasks by assigned pet name or completion state |
| Conflict handling | `Scheduler.detect_conflicts()` | Checks exact start time collisions and interval duration overlaps |
| Recurring tasks | `Task.get_next_occurrence()`, `Scheduler.mark_task_complete()` | Auto-generates next occurrence (+1 day for daily, +7 days for weekly) |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. **Owner & Pet Setup**: Register pet owner details and add multiple pets (e.g. Mochi the dog and Luna the cat).
2. **Task Creation**: Add daily, weekly, or one-off tasks with designated time, duration, and priority.
3. **Multi-Pet Aggregation**: The `Scheduler` queries `Owner.get_all_tasks()` to collect tasks across all household pets.
4. **Smart Scheduling & Conflicts**: Tasks are sorted chronologically; overlapping appointments trigger actionable warnings.
5. **Task Completion & Recurrence**: Marking a daily task complete generates tomorrow's instance automatically.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
