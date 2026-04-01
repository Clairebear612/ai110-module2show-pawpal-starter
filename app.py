import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A pet care scheduling assistant.")

st.divider()

# --- Owner & Pet setup ---
st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name_input = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(owner_name)
    pet = Pet(pet_name_input, species)
    st.session_state.owner.add_pet(pet)
    st.success(f"Added **{pet_name_input}** the {species} to {owner_name}'s profile.")

if "owner" in st.session_state:
    pets = st.session_state.owner.get_pets()
    if pets:
        st.caption(f"Pets on file: {', '.join(p.name for p in pets)}")

st.divider()

# --- Add a Task ---
st.subheader("Add a Task")

col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
with col1:
    task_description = st.text_input("Task description", value="Morning walk")
with col2:
    task_time = st.text_input("Time (e.g. 7:00 AM)", value="7:00 AM")
with col3:
    task_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Once"])
with col4:
    task_duration = st.number_input("Duration (min)", min_value=1, value=30)

if st.button("Add Task"):
    if "owner" not in st.session_state or not st.session_state.owner.get_pets():
        st.warning("Add a pet first before scheduling tasks.")
    else:
        pets = st.session_state.owner.get_pets()
        task = Task(task_description, task_time, task_frequency, duration_minutes=task_duration)
        pets[-1].add_task(task)
        st.success(f"Task **'{task_description}'** added to {pets[-1].name}.")

st.divider()

# --- Generate Schedule ---
st.subheader("Today's Schedule")

# Pet filter (shown only when there are pets to filter by)
if "owner" in st.session_state and st.session_state.owner.get_pets():
    pet_names = ["All Pets"] + [p.name for p in st.session_state.owner.get_pets()]
    filter_pet = st.selectbox("Filter by pet", pet_names, key="pet_filter")
else:
    filter_pet = "All Pets"

if st.button("Generate Schedule"):
    if "owner" not in st.session_state or not st.session_state.owner.get_pets():
        st.warning("Add a pet and tasks first.")
    else:
        st.session_state.show_schedule = True

if st.session_state.get("show_schedule") and "owner" in st.session_state:
    scheduler = Scheduler(st.session_state.owner)
    pet_name_arg = None if filter_pet == "All Pets" else filter_pet

    sorted_pending = scheduler.get_tasks_sorted_by_time(pet_name=pet_name_arg, status="pending")
    completed = scheduler.get_completed_tasks()

    # Use detect_conflicts() directly for structured conflict data.
    # Split into same-time vs. rolling overlap so we can give the owner
    # a different, actionable message for each case.
    all_conflicts = scheduler.detect_conflicts()
    same_time_conflicts = [
        (a, b) for a, b in all_conflicts if a[1].time == b[1].time
    ]
    rolling_conflicts = [
        (a, b) for a, b in all_conflicts if a[1].time != b[1].time
    ]

    if not sorted_pending and not completed:
        st.info("No tasks scheduled yet. Add some tasks above.")
    else:
        # --- Summary metrics ---
        m1, m2, m3 = st.columns(3)
        m1.metric("Pending", len(sorted_pending))
        m2.metric("Completed", len(completed))
        m3.metric("Conflicts", len(all_conflicts))

        # --- Conflict banner: shown at top so owner sees it before scrolling ---
        if all_conflicts:
            st.error(
                f"**{len(all_conflicts)} scheduling conflict(s) detected today.** "
                "Expand 'Scheduling Conflicts' below to see what needs attention."
            )

        st.divider()

        # --- Pending tasks with Mark Complete buttons ---
        if sorted_pending:
            st.markdown("#### Pending Tasks")
            h1, h2, h3, h4, h5 = st.columns([2, 2, 4, 2, 2])
            h1.markdown("**Time**")
            h2.markdown("**Pet**")
            h3.markdown("**Task**")
            h4.markdown("**Duration**")
            h5.markdown("")
            st.divider()
            for pname, task in sorted_pending:
                c1, c2, c3, c4, c5 = st.columns([2, 2, 4, 2, 2])
                c1.write(task.time)
                c2.write(pname)
                c3.write(task.description)
                c4.write(f"{task.duration_minutes} min")
                if c5.button("Done", key=f"complete_{pname}_{task.description}_{task.time}"):
                    scheduler.complete_task(pname, task)
                    st.rerun()
        else:
            st.success("All tasks for today are complete!")

        # --- Completed tasks: collapsed by default since they need no action ---
        if completed:
            with st.expander(f"Completed Tasks ({len(completed)})", expanded=False):
                st.table([
                    {"Pet": pname, "Task": task.description, "Frequency": task.frequency}
                    for pname, task in completed
                ])

        # --- Conflict details: structured, plain-language, actionable ---
        if all_conflicts:
            with st.expander(f"Scheduling Conflicts ({len(all_conflicts)})", expanded=True):
                st.caption(
                    "Adjust a task's start time to resolve each conflict. "
                    "Use the Add a Task form above to reschedule."
                )

                if same_time_conflicts:
                    st.markdown("**Same start time**")
                    for (pet_a, task_a), (pet_b, task_b) in same_time_conflicts:
                        if pet_a == pet_b:
                            msg = (
                                f"**{pet_a}** has two tasks starting at **{task_a.time}**: "
                                f"*{task_a.description}* and *{task_b.description}*. "
                                f"Only one can start at this time — shift one of them."
                            )
                        else:
                            msg = (
                                f"**{task_a.description}** ({pet_a}) and "
                                f"**{task_b.description}** ({pet_b}) are both scheduled for "
                                f"**{task_a.time}**. Make sure someone is available for each."
                            )
                        st.warning(msg)

                if rolling_conflicts:
                    st.markdown("**Overlapping tasks**")
                    for (pet_a, task_a), (pet_b, task_b) in rolling_conflicts:
                        overlap_min = (
                            task_a.get_time_minutes() + task_a.duration_minutes
                            - task_b.get_time_minutes()
                        )
                        msg = (
                            f"**{task_a.description}** ({pet_a}, {task_a.time}, "
                            f"{task_a.duration_minutes} min) runs into "
                            f"**{task_b.description}** ({pet_b}, {task_b.time}) "
                            f"by **{overlap_min} minute(s)**. "
                            f"Start *{task_b.description}* at least {overlap_min} min later."
                        )
                        st.warning(msg)
