import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add Pet"):
    if "owner" not in st.session_state:
        st.session_state.owner = Owner(owner_name)
    pet = Pet(pet_name, species)
    st.session_state.owner.add_pet(pet)
    st.success(f"Added {pet_name} the {species} to {owner_name}'s profile.")

st.divider()

st.markdown("### Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_description = st.text_input("Task description", value="Morning walk")
with col2:
    task_time = st.text_input("Time", value="7:00 AM")
with col3:
    task_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])

if st.button("Add Task"):
    if "owner" not in st.session_state or not st.session_state.owner.get_pets():
        st.warning("Add a pet first before scheduling tasks.")
    else:
        pets = st.session_state.owner.get_pets()
        task = Task(task_description, task_time, task_frequency)
        pets[-1].add_task(task)
        st.success(f"Task '{task_description}' added to {pets[-1].name}.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate Schedule"):
    if "owner" not in st.session_state or not st.session_state.owner.get_pets():
        st.warning("Add a pet and tasks first.")
    else:
        scheduler = Scheduler(st.session_state.owner)
        pending = scheduler.get_pending_tasks()
        completed = scheduler.get_completed_tasks()

        if not pending and not completed:
            st.info("No tasks scheduled yet.")
        else:
            st.markdown("#### Pending Tasks")
            for pet_name, task in pending:
                st.write(f"- [{task.time}] **{pet_name}** — {task.description} ({task.frequency})")

            st.markdown("#### Completed Tasks")
            if completed:
                for pet_name, task in completed:
                    st.write(f"- ~~{task.description}~~ ({pet_name})")
            else:
                st.caption("None completed yet.")
