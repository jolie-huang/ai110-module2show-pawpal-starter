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

PawPal+ includes a comprehensive unit test suite built with `pytest` in `tests/test_pawpal.py` to verify domain models, scheduling logic, and edge cases.

### Running Tests

Execute the test suite using either of the following commands:

```bash
# Run tests with Python module runner:
python -m pytest

# Run tests with detailed verbose output:
python -m pytest -v
```

### What the Tests Cover

The test suite contains 18 unit tests covering four core areas:

1. **Sorting Correctness**:
   - **Chronological Ordering**: Ensures tasks entered in random or out-of-order sequences are ordered from earliest to latest.
   - **Time Parsing & Normalization**: Confirms single-digit hours (`"8:00"`) correctly sort before double-digit hours (`"10:00"`), avoiding naive string comparison errors.
   - **Day Boundaries**: Tests extreme timestamps such as midnight (`"00:15"`) and end of day (`"23:45"`).
   - **Priority Sorting**: Verifies descending priority ordering (High &rarr; Medium &rarr; Low).

2. **Recurrence Logic**:
   - **Daily Rollover**: Confirms that marking a daily task complete sets `is_completed=True` on the original task, creates a new task instance for tomorrow (`today + 1 day`) with `is_completed=False`, and attaches it to the pet.
   - **Weekly Rollover**: Validates that weekly tasks advance by exactly 7 days (`today + 7 days`).
   - **One-Time Tasks**: Verifies non-recurring tasks (`frequency="once"`) do not spawn new occurrences upon completion.
   - **Overdue Task Anchoring**: Ensures overdue tasks from past dates anchor new occurrences to `today + 1 day` so tasks are never scheduled in the past.
   - **Idempotent Completion**: Ensures calling completion repeatedly on the same task does not create duplicate recurring entries for the same date.

3. **Conflict Detection**:
   - **Exact Duplicate Times**: Flags tasks scheduled at the exact same minute, categorizing them as either `[Same-Pet]` or `[Multi-Pet]`.
   - **Interval Overlaps**: Flags when a subsequent task starts before the preceding task's duration has ended (`start < end`).
   - **Back-to-Back Precision**: Confirms tasks starting at the exact minute an earlier task ends (e.g., 08:00–08:30 and 08:30–09:00) do **not** trigger false-positive warnings.
   - **Active Task Filtering**: Ensures already completed tasks do not trigger conflicts with pending tasks.

4. **Entity Management & Filtering**:
   - **Automatic Attribution**: Adding a task to a `Pet` automatically stamps the pet's name on the task.
   - **Multi-Pet Aggregation**: `Owner.get_all_tasks()` aggregates tasks across all owned pets seamlessly.
   - **Multi-Criteria Filtering**: Tests filtering by pet name, completion status, and combined criteria.
   - **Empty States**: Confirms empty owners, pets with no tasks, and empty schedules execute gracefully without raising exceptions.

### Sample Test Output

```text
============================= test session starts =============================
platform win32 -- Python 3.15.0, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\jolie\Downloads\codepath\ai110-module2show-pawpal-starter
collected 18 items

tests/test_pawpal.py::test_sorting_by_time_chronological PASSED          [  5%]
tests/test_pawpal.py::test_sorting_handles_single_digit_and_boundary_hours PASSED [ 11%]
tests/test_pawpal.py::test_sorting_by_priority PASSED                    [ 16%]
tests/test_pawpal.py::test_daily_recurrence_creates_next_day_task PASSED [ 22%]
tests/test_pawpal.py::test_weekly_recurrence_creates_seven_days_later PASSED [ 27%]
tests/test_pawpal.py::test_one_time_task_does_not_recur PASSED           [ 33%]
tests/test_pawpal.py::test_recurrence_overdue_task_anchored_to_today PASSED [ 38%]
tests/test_pawpal.py::test_recurrence_idempotency_prevents_duplicate_entries PASSED [ 44%]
tests/test_pawpal.py::test_conflict_detection_flags_exact_duplicate_times_same_pet PASSED [ 50%]
tests/test_pawpal.py::test_conflict_detection_flags_exact_duplicate_times_different_pets PASSED [ 55%]
tests/test_pawpal.py::test_conflict_detection_duration_overlap PASSED    [ 61%]
tests/test_pawpal.py::test_back_to_back_tasks_do_not_conflict PASSED     [ 66%]
tests/test_pawpal.py::test_completed_tasks_do_not_trigger_daily_conflicts PASSED [ 72%]
tests/test_pawpal.py::test_task_mark_complete PASSED                     [ 77%]
tests/test_pawpal.py::test_pet_task_addition_and_attribution PASSED      [ 83%]
tests/test_pawpal.py::test_owner_multi_pet_aggregation PASSED            [ 88%]
tests/test_pawpal.py::test_filtering_by_pet_and_status PASSED            [ 94%]
tests/test_pawpal.py::test_empty_states_handled_gracefully PASSED        [100%]

============================== 18 passed in 0.06s ==============================
```

**Confidence Level**: ⭐⭐⭐⭐⭐ (5/5 stars)

## 📐 Smarter Scheduling

PawPal+ includes four core algorithmic behaviors located in `pawpal_system.py` to keep daily pet routines organized, consistent, and collision-free:

### 1. Sorting Behavior
* **Methods**: `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()`
* **Implementation Details**:
  * `sort_by_time()` sorts tasks chronologically using Python's `sorted()` with a key that converts `"HH:MM"` 24-hour time strings into comparable `datetime` objects via `_parse_time()`.
  * Avoids string-comparison pitfalls (such as `"8:00" > "10:00"`) and safely orders tasks regardless of insertion order.
  * `sort_by_priority()` maps priorities (`high: 1`, `medium: 2`, `low: 3`) to order tasks by urgency during schedule crunch times.

### 2. Filtering Behavior
* **Methods**: `Scheduler.filter_tasks()`, `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()`
* **Implementation Details**:
  * `filter_tasks()` provides a unified multi-criteria filter in a single $O(N)$ pass. It can filter simultaneously by pet name (case-insensitive), completion status (`is_completed=True/False`), priority, and specific dates.
  * `filter_by_pet()` and `filter_by_status()` act as clean convenience wrappers that delegate to `filter_tasks()`, enabling individual pet views and pending task dashboards in both CLI and Streamlit.

### 3. Conflict Detection Logic
* **Method**: `Scheduler.detect_conflicts()`
* **Implementation Details**:
  * **Lightweight & Non-Blocking**: Instead of raising exceptions that would crash the app or block user view, the method returns a list of human-readable warning strings (`List[str]`).
  * **Sweep-Line Interval Check**: Sorts active schedule tasks chronologically and checks adjacent intervals. If the next task starts after or at the current task's end time, it breaks early.
  * **Scope Differentiation**: Explicitly categorizes collisions as:
    * **`[Same-Pet]`**: Flagging when an individual pet has duplicate simultaneous tasks (e.g. eating and meds at the same time).
    * **`[Multi-Pet]`**: Flagging caregiver bottlenecks when tasks across different pets overlap (e.g. walking the dog while on a cat vet call).
  * Catches both exact start-time collisions and interval overlaps (`t2_start < t1_end`).

### 4. Recurring Task Logic
* **Methods**: `Task.get_next_occurrence()`, `Scheduler.mark_task_complete()`
* **Implementation Details**:
  * `Task.get_next_occurrence()` calculates the next occurrence using Python's `datetime.timedelta`:
    * `"daily"`: Adds `timedelta(days=1)` (today + 1 day).
    * `"weekly"`: Adds `timedelta(days=7)` (today + 7 days).
    * `"once"`: Returns `None` (non-recurring).
  * Automatically handles calendar rollovers (month boundaries, leap years) and anchors overdue tasks to today so past tasks never spawn occurrences in the past.
  * `Scheduler.mark_task_complete()` handles the lifecycle: it marks the current task completed, generates the next occurrence, and attaches it to the appropriate pet with an **idempotency check** to prevent duplicate tasks if users toggle checkboxes multiple times.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. **Owner & Pet Setup**: Register pet owner details and add multiple pets (e.g. Mochi the dog and Luna the cat).
2. **Task Creation**: Add daily, weekly, or one-off tasks with designated time, duration, and priority.
3. **Multi-Pet Aggregation**: The `Scheduler` queries `Owner.get_all_tasks()` to collect tasks across all household pets.
4. **Smart Scheduling & Conflicts**: Tasks are sorted chronologically; overlapping appointments trigger actionable warnings.
5. **Task Completion & Recurrence**: Marking a daily task complete generates tomorrow's instance automatically.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
