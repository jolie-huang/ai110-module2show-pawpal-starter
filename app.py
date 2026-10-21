import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+ Pet Care Planner", page_icon="🐾", layout="wide")

# 1. Manage Application Memory via st.session_state
if "owner" not in st.session_state:
    initial_owner = Owner(name="Jordan")
    
    # Pre-seed with sample pets so the app is immediately testable
    mochi = Pet(name="Mochi", species="Dog", breed="Golden Retriever", age=3)
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=2)

    # Add sample routines
    mochi.add_task(Task(title="Morning Walk", time="08:00", duration_minutes=30, priority="high", frequency="daily"))
    mochi.add_task(Task(title="Breakfast & Meds", time="08:45", duration_minutes=15, priority="high", frequency="daily"))
    luna.add_task(Task(title="Vet Video Checkup", time="08:45", duration_minutes=30, priority="high", frequency="once"))
    luna.add_task(Task(title="Catnip Play Session", time="09:15", duration_minutes=25, priority="medium", frequency="daily"))

    initial_owner.add_pet(mochi)
    initial_owner.add_pet(luna)
    st.session_state.owner = initial_owner

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner=owner)

# Header
st.title("🐾 PawPal+ Smart Pet Care Planner")
st.caption(f"Logged in as Owner: **{owner.name}** | Managing {len(owner.pets)} pet(s)")

# Sidebar: Manage Household Pets
with st.sidebar:
    st.header("🐶 Household Pets")
    for pet in owner.pets:
        st.markdown(f"**{pet.name}** ({pet.species}, {pet.breed}, {pet.age} yrs) - `{len(pet.tasks)} tasks`")
    
    st.divider()
    st.subheader("Add a New Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name = st.text_input("Pet Name")
        new_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Other"])
        new_breed = st.text_input("Breed", value="Mixed")
        new_age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
        submit_pet = st.form_submit_button("Add Pet to Household")

        if submit_pet:
            if new_pet_name.strip():
                new_pet = Pet(name=new_pet_name.strip(), species=new_species, breed=new_breed, age=int(new_age))
                # Class method call to add pet to Owner
                owner.add_pet(new_pet)
                st.success(f"Added {new_pet.name} to {owner.name}'s household!")
                st.rerun()
            else:
                st.error("Please enter a valid pet name.")

# Main Layout Tabs
tab_schedule, tab_add_task, tab_all_tasks = st.tabs(["📅 Today's Smart Schedule", "➕ Schedule a Task", "📋 All Pet Routines"])

# Tab 1: Smart Daily Schedule
with tab_schedule:
    st.subheader("Smart Daily Schedule")
    st.caption("Tasks are aggregated across all pets, sorted chronologically, and checked for conflicts.")

    # Algorithmic Conflict Detection
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        st.error("⚠️ Schedule Conflicts Detected!")
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("✅ No schedule conflicts detected! All routines run smoothly.")

    # Daily Schedule Display
    daily_schedule = scheduler.get_daily_schedule()
    if daily_schedule:
        schedule_data = []
        for t in daily_schedule:
            schedule_data.append({
                "Time": t.time,
                "Pet": t.pet_name,
                "Task": t.title,
                "Duration": f"{t.duration_minutes} min",
                "Priority": t.priority.upper(),
                "Frequency": t.frequency.capitalize(),
                "Status": "Pending" if not t.is_completed else "Completed"
            })
        st.dataframe(schedule_data, use_container_width=True)

        st.subheader("💡 Plan Explanations")
        for exp in scheduler.explain_plan():
            st.markdown(f"- {exp}")
    else:
        st.info("No active tasks scheduled for today. Add tasks in the 'Schedule a Task' tab!")

# Tab 2: Add / Schedule a Task
with tab_add_task:
    st.subheader("Schedule a New Care Task")
    if not owner.pets:
        st.warning("Please add at least one pet in the sidebar first!")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                selected_pet_name = st.selectbox("Assign to Pet", [p.name for p in owner.pets])
                task_title = st.text_input("Task Title", value="Evening Walk")
                task_time = st.text_input("Scheduled Time (HH:MM in 24h)", value="18:00")
            with col2:
                task_duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=30, step=5)
                task_priority = st.selectbox("Priority", ["high", "medium", "low"], index=1)
                task_frequency = st.selectbox("Frequency", ["daily", "weekly", "once"], index=0)
            
            submit_task = st.form_submit_button("Add Task to Routine")

            if submit_task:
                target_pet = owner.get_pet(selected_pet_name)
                if target_pet:
                    new_task = Task(
                        title=task_title.strip(),
                        time=task_time.strip(),
                        duration_minutes=int(task_duration),
                        priority=task_priority,
                        frequency=task_frequency
                    )
                    # Class method call to add task to Pet
                    target_pet.add_task(new_task)
                    st.success(f"Added '{new_task.title}' for {target_pet.name} at {new_task.time}!")
                    st.rerun()

# Tab 3: All Routines & Task Completion
with tab_all_tasks:
    st.subheader("All Household Tasks & Actions")
    all_tasks = owner.get_all_tasks()
    
    if not all_tasks:
        st.info("No tasks recorded yet.")
    else:
        # Filter options
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            pet_filter = st.selectbox("Filter by Pet", ["All Pets"] + [p.name for p in owner.pets])
        with filter_col2:
            status_filter = st.selectbox("Filter by Status", ["All Tasks", "Pending Only", "Completed Only"])

        filtered_tasks = all_tasks
        if pet_filter != "All Pets":
            filtered_tasks = scheduler.filter_by_pet(pet_filter)
        if status_filter == "Pending Only":
            filtered_tasks = [t for t in filtered_tasks if not t.is_completed]
        elif status_filter == "Completed Only":
            filtered_tasks = [t for t in filtered_tasks if t.is_completed]

        st.caption(f"Showing {len(filtered_tasks)} task(s):")
        for idx, task in enumerate(filtered_tasks):
            col_info, col_action = st.columns([4, 1])
            with col_info:
                st.markdown(
                    f"**{task.time}** — **{task.title}** for *{task.pet_name}* "
                    f"({task.duration_minutes}m, Priority: `{task.priority}`, Frequency: `{task.frequency}`) | "
                    f"Status: **{'✅ Done' if task.is_completed else '⏳ Pending'}**"
                )
            with col_action:
                if not task.is_completed:
                    if st.button("Mark Complete", key=f"complete_{idx}_{task.title}_{task.time}"):
                        # Class method call to complete and handle recurring task
                        next_task = scheduler.mark_task_complete(task)
                        if next_task:
                            st.toast(f"Recurring task created for {next_task.pet_name} on {next_task.date} at {next_task.time}!")
                        st.rerun()
