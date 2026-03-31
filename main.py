from pawpal_system import Task, Pet, Owner, Scheduler

# --- Setup ---
owner = Owner("Clarise")

dog = Pet("Bella", "Dog")
cat = Pet("Mochi", "Cat")

# --- Tasks for Bella ---
dog.add_task(Task("Morning walk on leash", "7:00 AM", "Daily"))
dog.add_task(Task("Feed chicken and rice", "8:00 AM", "Daily"))

# --- Tasks for Mochi ---
cat.add_task(Task("Bathe with oatmeal shampoo", "10:00 AM", "Weekly"))
cat.add_task(Task("Feed wet food", "12:00 PM", "Daily"))

# --- Register pets to owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- Scheduler ---
scheduler = Scheduler(owner)

# --- Print Today's Schedule ---
print("=" * 40)
print("       PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 40)

for pet_name, task in scheduler.get_all_tasks():
    status = "✓" if task.is_complete else "○"
    print(f"[{status}] {task.time:<12} {pet_name:<8} — {task.description} ({task.frequency})")

print("=" * 40)
print(f"Total tasks: {len(scheduler.get_all_tasks())}")
print(f"Pending:     {len(scheduler.get_pending_tasks())}")
print(f"Completed:   {len(scheduler.get_completed_tasks())}")
print("=" * 40)
