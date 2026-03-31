from pawpal_system import Task, Pet, Owner, Scheduler

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
owner = Owner("Clarise")

dog = Pet("Bella", "Dog")
cat = Pet("Mochi", "Cat")

# Tasks added OUT OF ORDER intentionally to test sorting
dog.add_task(Task("Feed chicken and rice",  "8:00 AM",  "Daily",  duration_minutes=20))
dog.add_task(Task("Evening walk on leash",  "5:00 PM",  "Daily",  duration_minutes=45))
dog.add_task(Task("Morning walk on leash",  "7:00 AM",  "Daily",  duration_minutes=45))  # earliest, added last

cat.add_task(Task("Feed wet food",              "7:20 AM",  "Daily",  duration_minutes=20))  # overlaps Bella's walk
cat.add_task(Task("Bathe with oatmeal shampoo", "10:00 AM", "Weekly", duration_minutes=30))
cat.add_task(Task("Afternoon nap check",        "2:00 PM",  "Once",   duration_minutes=10))

# --- Intentional conflicts for verification ---
# Same-pet conflict: Bella has two tasks at 8:00 AM
dog.add_task(Task("Vet check-up", "8:00 AM", "Once", duration_minutes=60))
# Cross-pet conflict: both pets scheduled at 10:00 AM
dog.add_task(Task("Grooming session", "10:00 AM", "Once", duration_minutes=30))

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)

# ---------------------------------------------------------------------------
# 1. Unsorted (insertion order) — shows why sorting is needed
# ---------------------------------------------------------------------------
print("=" * 50)
print("  RAW ORDER (insertion order — unsorted)")
print("=" * 50)
for pet_name, task in scheduler.get_all_tasks():
    print(f"  {task.time:<12} {pet_name:<8} — {task.description}")

# ---------------------------------------------------------------------------
# 2. Sorted by time — all pets
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print("  SORTED BY TIME — all pets")
print("=" * 50)
for pet_name, task in scheduler.get_tasks_sorted_by_time():
    status = "✓" if task.is_complete else "○"
    print(f"  [{status}] {task.time:<12} {pet_name:<8} — {task.description}")

# ---------------------------------------------------------------------------
# 3. Filter by pet name — Bella only
# ---------------------------------------------------------------------------
print("\n--- Filter: Bella's tasks (sorted) ---")
for pet_name, task in scheduler.get_tasks_sorted_by_time(pet_name="Bella"):
    print(f"  {task.time:<12} {pet_name} — {task.description}")

# ---------------------------------------------------------------------------
# 4. Filter by pet name — Mochi only
# ---------------------------------------------------------------------------
print("\n--- Filter: Mochi's tasks (sorted) ---")
for pet_name, task in scheduler.get_tasks_sorted_by_time(pet_name="Mochi"):
    print(f"  {task.time:<12} {pet_name} — {task.description}")

# ---------------------------------------------------------------------------
# 5. Mark some tasks complete, then filter by status
# ---------------------------------------------------------------------------
dog.get_tasks()[0].mark_complete()   # Feed chicken and rice → done
cat.get_tasks()[0].mark_complete()   # Feed wet food → done

print("\n--- Filter: Completed tasks ---")
for pet_name, task in scheduler.get_completed_tasks():
    print(f"  [✓] {pet_name:<8} {task.time:<12} {task.description}")

print("\n--- Filter: Pending tasks ---")
for pet_name, task in scheduler.filter_tasks(status="pending"):
    print(f"  [○] {pet_name:<8} {task.time:<12} {task.description}")

# ---------------------------------------------------------------------------
# 6. Combined filter — Bella, pending only
# ---------------------------------------------------------------------------
print("\n--- Filter: Bella — pending only ---")
for pet_name, task in scheduler.get_tasks_sorted_by_time(pet_name="Bella", status="pending"):
    print(f"  [○] {task.time:<12} {task.description}")

# ---------------------------------------------------------------------------
# 7. Conflict detection (lightweight — always returns warnings, never crashes)
# ---------------------------------------------------------------------------
print("\n--- Conflict Detection: Today ---")
warnings = scheduler.check_conflicts()
if warnings:
    for warning in warnings:
        print(f"  {warning}")
else:
    print("  No conflicts detected.")

# ---------------------------------------------------------------------------
# 8. Auto-schedule next occurrence on complete
# ---------------------------------------------------------------------------
print("\n--- Recurring Auto-Schedule ---")
walk_task = dog.get_tasks()[2]  # Morning walk on leash (Daily)
print(f"  Completing: '{walk_task.description}' ({walk_task.frequency})")
next_task = scheduler.complete_task("Bella", walk_task)
if next_task:
    print(f"  Auto-scheduled next: '{next_task.description}' due {next_task.due_date}")
else:
    print("  No recurrence (Once task).")

bathe_task = cat.get_tasks()[1]  # Bathe (Weekly)
print(f"  Completing: '{bathe_task.description}' ({bathe_task.frequency})")
next_task = scheduler.complete_task("Mochi", bathe_task)
if next_task:
    print(f"  Auto-scheduled next: '{next_task.description}' due {next_task.due_date}")

nap_task = cat.get_tasks()[2]   # Afternoon nap check (Once)
print(f"  Completing: '{nap_task.description}' ({nap_task.frequency})")
next_task = scheduler.complete_task("Mochi", nap_task)
if next_task:
    print(f"  Auto-scheduled next: '{next_task.description}'")
else:
    print(f"  No recurrence (Once task) — not re-added.")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 50)
print(f"  Total    : {len(scheduler.get_all_tasks())}")
print(f"  Pending  : {len(scheduler.get_pending_tasks())}")
print(f"  Completed: {len(scheduler.get_completed_tasks())}")
print(f"  Conflicts: {len(warnings)}")
print("=" * 50)
