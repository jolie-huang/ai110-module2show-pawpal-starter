# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- The 3 core actions a user should be able to perform are entering basic owner and pet info, adding/editing tasks, generating a daily plan based on variables like constraints and priorities. This plan should be explained clearly. there also should be tests on the backend to ensure everything is working in its intended purpose.
-For the main objects needed for the system, you would need the following:
owner, pet, task, plan
The attributes would probably look like this:
Owner: name
Pet: name, breed, age
Task: name, duration, frequency, date, urgency/priority
Plan: name, number of tasks
The methods would probably look like this:
Owner: edit info
Pet: edit info
Task: add task, edit task
Plan: edit plan, view plan, view explanation


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

My design changed in two main ways:
- The first was how tasks get linked back to their pet. I updated `Pet.add_task()` so that if a task doesn't already have a `pet_name`, it automatically gets set to the pet's name. The reason is that `Owner.get_all_tasks()` pulls every pet's tasks into one big list for the `Scheduler`, and at that point each task needs to know which pet it belongs to. Without this, a multi-pet schedule would lose track of whose task was whose.
- The second was how recurring tasks get created. I kept `Task` independent by having `Task.get_next_occurrence()` just build and return a fresh `Task`, and then let `Scheduler.mark_task_complete()` handle adding it to the pet's task list. If `Task` held a reference back to `Pet` or `Owner`, it would create circular dependencies and break encapsulation. Letting the `Scheduler` coordinate it keeps each class focused on one job.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Clock time mattered most. A pet owner lives by the clock, and a plan that isn't in chronological order is just confusing. A lot of pet routines, like potty breaks and morning meals, depend on happening at the right time, so sorting by time was the foundation everything else sits on.
Conflict detection came second, as a kind of guardrail. One person can't walk the dog and feed the cat at 8:00 at the same moment, so the scheduler flags overlaps to nudge the owner into staggering things and keep the plan realistic.
Priority came last, as the tie-breaker. When times clash or the owner is short on time, priority decides what has to happen and what can slide. Health-critical stuff like medications should never get pushed back, while something like brushing or training can easily wait.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler handles conflicts with warnings instead of rejecting tasks or throwing errors when times overlap. It also keeps whatever start times the owner set, rather than trying to shuffle tasks into open slots on its own.
I went this way because in real pet care, a lot of things happen at the same time. You might put out food for the cat while brushing the dog, or a couple of family members might each be looking after a different pet. If the scheduler threw hard errors or moved things around automatically, it could push something time-critical, like morning meds or a feeding, into a bad window. Warnings that don't block anything let the owner see exactly what's going on and stay in control, and they keep the scheduling logic predictable and easy to trust.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI in a few different ways on this project.
At the start, I used it to help me plan the design. I gave it my rough requirements and it helped me turn them into a UML class diagram, so I could see how `Owner`, `Pet`, `Task`, and `Scheduler` fit together before writing any code.
Then I had it set up the basic `@dataclass` skeletons with type hints and safe defaults, like `field(default_factory=list)`, so I wouldn't run into Python's mutable default argument problem.
Before building out the real logic, I asked it to look over the skeletons for problems. It caught a couple things I missed. Tasks would lose track of which pet they belonged to once they got pooled into one schedule, and `Task` managing its own `Pet` could cause circular dependencies.
After that, it helped me write the actual logic. For sorting, we used `datetime.strptime` so "8:00" doesn't end up after "10:00" like it would with plain strings. For conflicts, we used `timedelta` to check if tasks overlap in duration, not just start at the same time. I also had it set up a CLI demo (`main.py`) and a `pytest` suite (`tests/test_pawpal.py`) so I could test the backend before touching the frontend.
The prompts that helped the most were:
- Asking how the `Scheduler` could get all the tasks from the owner's pets without breaking encapsulation or the Law of Demeter.
- Asking it to review my class skeleton for missing relationships, tight coupling, or anything that might cause problems later.
- Asking how to catch conflicts based on overlapping durations and show a friendly warning instead of crashing.
- Asking it to write pytest tests for task status changes and task list accumulation.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When we got to conflict detection, it first suggested raising a custom error (ScheduleConflictError) whenever two tasks overlapped. I didn't like that, because crashing the whole thing is a bad experience. In real life, someone might do two things at once on purpose, like letting the dog out while getting the cat's food ready. If it crashed, they wouldn't even see their plan. So I changed it so Scheduler.detect_conflicts() just returns a list of warning messages. The schedule still shows up like normal, and you get a heads-up about the overlap.

I also didn't trust the AI's code just because it looked right. For sorting times, I tested what happens with something like "8:00" vs. "10:00". Comparing them as plain strings got it wrong since '8' is bigger than '1', which is why we switched to datetime.strptime. For the multi-pet and recurring task stuff, I ran little test scripts and the pytest suite (python -m pytest) in the project's virtual environment. Once the tests passed, I felt pretty good that everything was working together the way it should.
---
## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested four main things.

**Sorting.** I added tasks completely out of order (like 18:00, 08:30, and 12:00) to make sure they came out in the right order. I also tried "8:00" vs "10:00" and edge times like "00:15" and "23:45" to be sure the times were being parsed with `datetime.strptime` and not compared as plain text. I checked priority sorting too (high, then medium, then low).

**Recurring tasks.** I checked that finishing a daily task creates tomorrow's task, not completed yet, and adds it to the pet's list. Weekly tasks move forward 7 days, and one-time tasks don't repeat. I also tested that an overdue task bases its next date on today instead of scheduling something in the past, and that completing the same task more than once doesn't create duplicates.

**Conflicts.** I tested tasks starting at the exact same time, both for the same pet (`[Same-Pet]`) and for different pets (`[Multi-Pet]`). I also tested overlaps by duration, like a task starting at 08:20 in the middle of an 08:00 to 08:30 block. Back-to-back tasks (08:00 to 08:30, then 08:30 to 09:00) shouldn't trigger a warning, so I checked that too. And completed tasks shouldn't conflict with pending ones, so I tested that as well.

**Pet names and empty cases.** I checked that `Pet.add_task()` automatically puts the pet's name on the task, and that `Owner.get_all_tasks()` combines tasks from all pets without losing track of whose is whose. I also tried an owner with no pets and a pet with no tasks to make sure nothing breaks.

These tests mattered because pet care depends on good timing, like meds and meals. If "8:00" sorted after "10:00", morning routines would show up after night ones. If recurring tasks broke, owners would have to re-enter their everyday stuff every morning. And if conflict detection crashed on overlaps or gave false warnings on back-to-back tasks, the app would be annoying and hard to trust.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm confident it works, so 5 out of 5 stars. The pytest suite in `tests/test_pawpal.py` has 18 tests, and they all pass in about 0.06 seconds when I run `python -m pytest`. They cover the normal cases and some edge cases across all four classes (`Owner`, `Pet`, `Task`, and `Scheduler`). I also used Python's built-in `datetime.strptime` and `timedelta` instead of slicing strings by hand, which is a lot less fragile. And each class has its own job: `Task` figures out date offsets, `Pet` manages its own list and stamps its name on tasks, `Owner` pulls everything together, and `Scheduler` coordinates it all.

If I had more time, here's what I'd test next:

- **Tasks that cross midnight.** Say a task starts at 23:30 and lasts 60 minutes, so it runs into 00:30 the next day. I'd want to see how the overlap check and the daily view handle that. This would be my first priority.
- **Month, year, and leap-year rollovers.** `timedelta` should handle these on its own, but I'd still write tests for things like Feb 28 to Feb 29 on a leap year and Dec 31 to Jan 1, just to make sure the dates show up correctly.
- **Other repeat schedules.** Things like every two weeks, once a month (like flea and tick medicine on the 1st), or something custom like every 3 days.
- **Renaming or deleting a pet.** I'd check what happens to tasks that are already scheduled if a pet's name changes or the pet gets removed.
- **Two people editing at once.** If two family members check off or edit tasks at the same moment in different browser tabs, Streamlit could run into race conditions, so I'd want to test that.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most happy with how clean the class relationships turned out, especially between Task, Pet, and Scheduler. Recurring tasks looked like they could get messy at first, because a task needs to know which pet it belongs to, but if Task held a direct reference to Pet or Owner, I'd have ended up with circular imports and tightly tangled code. Instead, Task.get_next_occurrence() just builds and returns a fresh Task using timedelta, and Scheduler.mark_task_complete() looks up the pet and attaches the new task, with a check to avoid duplicates. 

I'm also happy with how conflict detection came out. It doesn't crash the app or move tasks around without asking. It gives you warnings that tell you whether the clash is for the same pet or across multiple pets, so owners get a helpful heads-up and stay in control. Hooking that into the Streamlit UI with live status tiles, plus having 18 passing unit tests, made me feel good about the final build.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Saving data: Right now everything lives in st.session_state, so if the Streamlit server restarts or the browser tab gets cleared, it all resets to the default pets and tasks. Adding something simple like SQLite or a JSON file would let it remember your schedule over weeks and months.
One-click conflict fixing: The scheduler spots collisions and gives a tip, like moving a task 15 minutes, but you still have to edit the task yourself. I'd add a "Resolve Conflict" button that finds the next open slot based on priority and offers to shift the time for you.
More repeat options. Right now it's just daily and weekly. I'd add things like specific days (Mon/Wed/Fri agility training), monthly (flea and tick meds on the 1st), or every N days.
Tasks that cross midnight: A task that runs from 23:30 to 00:30 should show up properly across multi-day views.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI is great for speeding things up but I still have to be the one making the design and user experience decisions. When we started on conflict detection, the AI's first idea was to throw a hard ScheduleConflictError and stop whenever two tasks overlapped. That's valid Python, but for a real pet owner it would just be a crash screen instead of their daily plan. 

I also learned not to trust AI code without checking it, especially for edge cases like comparing "8:00" and "10:00" as strings, or what happens with overdue task rollovers. Testing each piece in pytest showed me that AI works best when you pair it with solid tests.