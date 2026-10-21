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

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
