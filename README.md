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

## Smarter Scheduling

The `Scheduler` class goes beyond a basic task list with four algorithmic features:

**Sort by time**
Tasks are sorted chronologically using `get_tasks_sorted_by_time()`. Time strings like `"7:00 AM"` are converted to minutes since midnight so they compare correctly — string sorting alone would put `"12:00 PM"` before `"7:00 AM"`.

**Filter by pet or status**
`filter_tasks(pet_name, status)` lets you narrow the schedule to a specific pet, only pending tasks, only completed tasks, or any combination. Both filters stack.

**Recurring task expansion**
`expand_recurring_tasks(days)` projects the schedule forward across multiple days. Daily tasks appear every day; Weekly tasks appear every 7th day; Once tasks appear only on day 0.

**Conflict detection**
Two complementary detectors surface scheduling problems without crashing:
- `detect_conflicts()` — catches tasks whose time windows overlap (e.g. a 45-minute walk and a feed scheduled 20 minutes later).
- `detect_same_time_conflicts()` — catches tasks with the exact same start time, labelled `same_pet` or `cross_pet`.
- `check_conflicts()` — runs both detectors and returns plain warning strings. Safe to call at any time; errors are caught and reported rather than raised.

**Auto-scheduling next occurrence**
`complete_task(pet_name, task)` marks a task done and automatically creates the next occurrence for Daily and Weekly tasks, with a calculated `due_date`. Once tasks complete without creating a follow-up.

---

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
