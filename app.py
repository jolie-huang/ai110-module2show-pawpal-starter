"""
PawPal+ Streamlit Application.
Interactive UI connecting domain entities (Owner, Pet, Task) to the Scheduler engine.
"""

from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(
    page_title="PawPal+ Smart Pet Planner",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for clean badges and readable metrics
st.markdown(
    """
    <style>
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    .conflict-card {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 5px solid #ff9800;
        background-color: #fff9e6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==============================================================================
# 1. APPLICATION STATE INITIALIZATION
# ==============================================================================
if "owner" not in st.session_state:
    initial_owner = Owner(name="Jordan")

    # Pre-seed with diverse sample pets and tasks so scheduling features are immediately visible
    mochi = Pet(name="Mochi", species="Dog", breed="Golden Retriever", age=3)
    luna = Pet(name="Luna", species="Cat", breed="Siamese", age=2)

    # Mochi routines (includes intentional overlap for demoing conflict detection)
    mochi.add_task(
        Task(
            title="Morning Walk & Potty",
            time="08:00",
            duration_minutes=30,
            priority="high",
            frequency="daily",
        )
    )
    mochi.add_task(
        Task(
            title="Breakfast & Supplements",
            time="08:45",
            duration_minutes=15,
            priority="high",
            frequency="daily",
        )
    )
    mochi.add_task(
        Task(
            title="Brush Coat & Grooming",
            time="14:00",
            duration_minutes=20,
            priority="medium",
            frequency="weekly",
        )
    )

    # Luna routines (08:45 creates an exact multi-pet conflict with Mochi's breakfast)
    luna.add_task(
        Task(
            title="Vet Video Checkup",
            time="08:45",
            duration_minutes=30,
            priority="high",
            frequency="once",
        )
    )
    luna.add_task(
        Task(
            title="Catnip Play Session",
            time="09:15",
            duration_minutes=25,
            priority="medium",
            frequency="daily",
        )
    )

    initial_owner.add_pet(mochi)
    initial_owner.add_pet(luna)
    st.session_state.owner = initial_owner

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner=owner)


# ==============================================================================
# 2. SIDEBAR: HOUSEHOLD PET MANAGEMENT
# ==============================================================================
with st.sidebar:
    st.header("🐶 Household Pets")
    for pet in owner.pets:
        with st.container():
            st.markdown(
                f"**{pet.name}** ({pet.species} • {pet.breed} • {pet.age}y)\n\n"
                f"Tasks assigned: `{len(pet.tasks)}`"
            )
            st.divider()

    st.subheader("Add a New Pet")
    with st.form("add_pet_form", clear_on_submit=True):
        new_pet_name = st.text_input("Pet Name", placeholder="e.g. Milo")
        new_species = st.selectbox("Species", ["Dog", "Cat", "Bird", "Rabbit", "Reptile", "Other"])
        new_breed = st.text_input("Breed", value="Mixed")
        new_age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)
        submit_pet = st.form_submit_button("➕ Register Pet")

        if submit_pet:
            if new_pet_name.strip():
                new_pet = Pet(
                    name=new_pet_name.strip(),
                    species=new_species,
                    breed=new_breed.strip(),
                    age=int(new_age),
                )
                owner.add_pet(new_pet)
                st.success(f"Registered {new_pet.name} in {owner.name}'s household!")
                st.rerun()
            else:
                st.error("Please provide a valid pet name.")


# ==============================================================================
# 3. TOP DASHBOARD METRICS
# ==============================================================================
st.title("🐾 PawPal+ Smart Pet Planner")
st.caption(f"Household Coordinator: **{owner.name}** | Active Care Schedule")

all_tasks = scheduler.get_all_tasks()
pending_tasks = scheduler.filter_by_status(is_completed=False)
completed_tasks = scheduler.filter_by_status(is_completed=True)
conflicts = scheduler.detect_conflicts()

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("🐾 Registered Pets", len(owner.pets))
col_m2.metric("⏳ Pending Today", len(pending_tasks))
col_m3.metric("✅ Completed", len(completed_tasks))
col_m4.metric(
    "⚠️ Active Conflicts",
    len(conflicts),
    delta="Action Required" if conflicts else "Smooth Schedule",
    delta_color="inverse" if conflicts else "normal",
)

st.markdown("---")


# ==============================================================================
# 4. MAIN WORKSPACE TABS
# ==============================================================================
tab_schedule, tab_add_task, tab_all_routines = st.tabs(
    ["📅 Smart Daily Schedule", "➕ Add Care Task", "📋 Routine Manager & Completion"]
)


# ------------------------------------------------------------------------------
# TAB 1: SMART DAILY SCHEDULE
# ------------------------------------------------------------------------------
with tab_schedule:
    st.subheader("Today's Optimized Schedule")
    st.caption("Aggregates routines across all pets, detects conflicts, and orders tasks algorithmically.")

    # A. Conflict Presentation (Actionable & Informative)
    if conflicts:
        st.warning(f"⚠️ **Schedule Conflicts Detected ({len(conflicts)})** — Review timing below to avoid overlap.")
        with st.expander("🔍 Conflict Details & Resolution Guidance", expanded=True):
            for conflict in conflicts:
                is_same_pet = "Same-Pet" in conflict
                badge = "🔴 Same-Pet Collision" if is_same_pet else "🟡 Multi-Pet Caregiver Bottleneck"
                st.markdown(f"**{badge}**")
                st.info(f"{conflict}\n\n*💡 Tip: {'Stagger start times so the pet can finish their prior activity.' if is_same_pet else 'Delegate one pet routine or shift one start time by 15-30 minutes.'}*")
    else:
        st.success("✅ **No schedule conflicts detected!** All scheduled routines run seamlessly.")

    # B. Sorting & Display Controls
    ctrl_col1, ctrl_col2 = st.columns([2, 1])
    with ctrl_col1:
        sort_mode = st.radio(
            "Sort Schedule By:",
            ["Chronological (Time: Earliest ➔ Latest)", "Urgency (Priority: High ➔ Med ➔ Low)"],
            horizontal=True,
        )
    with ctrl_col2:
        pet_view_filter = st.selectbox(
            "View Schedule For:",
            ["All Pets"] + [p.name for p in owner.pets],
            key="schedule_pet_filter",
        )

    # Retrieve and sort active daily schedule using Scheduler methods
    if "Chronological" in sort_mode:
        active_schedule = scheduler.get_daily_schedule()
    else:
        active_schedule = scheduler.sort_by_priority(pending_tasks)

    if pet_view_filter != "All Pets":
        active_schedule = scheduler.filter_tasks(pet_name=pet_view_filter, tasks=active_schedule)

    # C. Professional Table Display
    if active_schedule:
        table_rows = []
        for t in active_schedule:
            # Calculate end time for clear duration visualization
            try:
                start_dt = datetime.strptime(t.time, "%H:%M")
                end_dt = start_dt + timedelta(minutes=t.duration_minutes)
                time_range = f"{t.time} - {end_dt.strftime('%H:%M')}"
            except ValueError:
                time_range = t.time

            priority_icon = {"high": "🔴 High", "medium": "🟡 Med", "low": "🟢 Low"}.get(
                t.priority.lower(), t.priority.capitalize()
            )

            table_rows.append(
                {
                    "Time Window": time_range,
                    "Pet": t.pet_name,
                    "Activity": t.title,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": priority_icon,
                    "Frequency": t.frequency.capitalize(),
                    "Due Date": t.date,
                }
            )

        df_schedule = pd.DataFrame(table_rows)
        st.dataframe(df_schedule, use_container_width=True, hide_index=True)

        # D. Plan Explanations
        with st.expander("💡 Algorithmic Plan Explanations", expanded=False):
            st.markdown("Here is how the Scheduler organized today's tasks and why:")
            for reason in scheduler.explain_plan():
                st.markdown(f"- {reason}")
    else:
        st.info("No active tasks found for the selected view.")


# ------------------------------------------------------------------------------
# TAB 2: SCHEDULE A TASK
# ------------------------------------------------------------------------------
with tab_add_task:
    st.subheader("Add a New Routine to the Schedule")

    if not owner.pets:
        st.warning("Please register at least one pet in the sidebar first!")
    else:
        with st.form("new_task_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                assigned_pet = st.selectbox("Assign to Pet", [p.name for p in owner.pets])
                title = st.text_input("Task Title", placeholder="e.g. Afternoon Play & Fetch")
                time_val = st.text_input("Start Time (24h HH:MM)", value="10:00")
            with f_col2:
                duration = st.number_input("Duration (minutes)", min_value=5, max_value=240, value=30, step=5)
                priority = st.selectbox("Priority Level", ["high", "medium", "low"], index=1)
                frequency = st.selectbox("Recurrence Frequency", ["daily", "weekly", "once"], index=0)

            submit_new_task = st.form_submit_button("➕ Schedule Task")

            if submit_new_task:
                if not title.strip():
                    st.error("Please enter a valid task title.")
                else:
                    pet_obj = owner.get_pet(assigned_pet)
                    if pet_obj:
                        new_task = Task(
                            title=title.strip(),
                            time=time_val.strip(),
                            duration_minutes=int(duration),
                            priority=priority,
                            frequency=frequency,
                        )
                        # Domain method: assigns task and sets pet attribution
                        pet_obj.add_task(new_task)
                        st.success(f"Scheduled '{new_task.title}' for {pet_obj.name} at {new_task.time}!")
                        st.rerun()


# ------------------------------------------------------------------------------
# TAB 3: ROUTINE MANAGER & COMPLETION
# ------------------------------------------------------------------------------
with tab_all_routines:
    st.subheader("Manage Routines & Complete Tasks")
    st.caption("Filter tasks, check off completed care items, and watch recurring tasks automatically roll over.")

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        f_pet = st.selectbox("Filter by Pet", ["All Pets"] + [p.name for p in owner.pets], key="f_pet_key")
    with filter_col2:
        f_status = st.selectbox("Filter by Status", ["All Tasks", "Pending Only", "Completed Only"], key="f_status_key")

    # Use Scheduler.filter_tasks() directly
    is_comp_arg = None
    if f_status == "Pending Only":
        is_comp_arg = False
    elif f_status == "Completed Only":
        is_comp_arg = True

    managed_tasks = scheduler.filter_tasks(pet_name=f_pet, is_completed=is_comp_arg)

    if not managed_tasks:
        st.info("No tasks match the selected filter criteria.")
    else:
        st.markdown(f"**Showing {len(managed_tasks)} task(s):**")
        for idx, task in enumerate(managed_tasks):
            with st.container():
                c_details, c_button = st.columns([4, 1])
                with c_details:
                    status_badge = "✅ Completed" if task.is_completed else "⏳ Pending"
                    prio_badge = {"high": "🔴 HIGH", "medium": "🟡 MEDIUM", "low": "🟢 LOW"}.get(
                        task.priority.lower(), task.priority.upper()
                    )
                    st.markdown(
                        f"**{task.time}** — **{task.title}** ({task.pet_name}) | "
                        f"⏱️ `{task.duration_minutes}m` | Priority: `{prio_badge}` | Frequency: `{task.frequency}` | "
                        f"Status: **{status_badge}** | Due: `{task.date}`"
                    )
                with c_button:
                    if not task.is_completed:
                        if st.button("Complete Task", key=f"btn_comp_{idx}_{task.title}_{task.time}"):
                            # Coordinates completion & recurring task creation
                            next_task = scheduler.mark_task_complete(task)
                            if next_task:
                                st.success(
                                    f"Completed! Next '{next_task.title}' auto-scheduled for "
                                    f"{next_task.pet_name} on {next_task.date} at {next_task.time}."
                                )
                            else:
                                st.info(f"Marked '{task.title}' as completed.")
                            st.rerun()
                st.divider()
