import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# --- Task tests ---

def test_task_defaults_to_incomplete():
    task = Task("Morning walk", "7:00 AM", "Daily")
    assert task.is_complete == False

def test_task_mark_complete():
    task = Task("Morning walk", "7:00 AM", "Daily")
    task.mark_complete()
    assert task.is_complete == True

def test_task_mark_incomplete():
    task = Task("Morning walk", "7:00 AM", "Daily")
    task.mark_complete()
    task.mark_incomplete()
    assert task.is_complete == False


# --- Pet tests ---

def test_pet_add_task():
    pet = Pet("Bella", "Dog")
    task = Task("Feed", "8:00 AM", "Daily")
    pet.add_task(task)
    assert task in pet.get_tasks()

def test_pet_remove_task():
    pet = Pet("Bella", "Dog")
    task = Task("Feed", "8:00 AM", "Daily")
    pet.add_task(task)
    pet.remove_task(task)
    assert task not in pet.get_tasks()


# --- Owner tests ---

def test_owner_add_pet():
    owner = Owner("Alex")
    pet = Pet("Bella", "Dog")
    owner.add_pet(pet)
    assert pet in owner.get_pets()

def test_owner_remove_pet():
    owner = Owner("Alex")
    pet = Pet("Bella", "Dog")
    owner.add_pet(pet)
    owner.remove_pet(pet)
    assert pet not in owner.get_pets()

def test_owner_get_all_tasks():
    owner = Owner("Alex")
    pet = Pet("Bella", "Dog")
    task = Task("Walk", "7:00 AM", "Daily")
    pet.add_task(task)
    owner.add_pet(pet)
    all_tasks = owner.get_all_tasks()
    assert len(all_tasks) == 1
    assert all_tasks[0] == ("Bella", task)


# --- Two required tests ---

def test_task_completion_changes_status():
    # Task Completion: calling mark_complete() changes is_complete to True
    task = Task("Bathe with oatmeal shampoo", "10:00 AM", "Weekly")
    assert task.is_complete == False
    task.mark_complete()
    assert task.is_complete == True

def test_task_addition_increases_pet_task_count():
    # Task Addition: adding a task to a Pet increases that pet's task count
    pet = Pet("Bella", "Dog")
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task("Morning walk on leash", "7:00 AM", "Daily"))
    assert len(pet.get_tasks()) == 1
    pet.add_task(Task("Feed chicken and rice", "8:00 AM", "Daily"))
    assert len(pet.get_tasks()) == 2


# --- Scheduler tests ---

def test_scheduler_get_pending_tasks():
    owner = Owner("Alex")
    pet = Pet("Bella", "Dog")
    task = Task("Walk", "7:00 AM", "Daily")
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert len(scheduler.get_pending_tasks()) == 1

def test_scheduler_get_completed_tasks():
    owner = Owner("Alex")
    pet = Pet("Bella", "Dog")
    task = Task("Walk", "7:00 AM", "Daily")
    task.mark_complete()
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert len(scheduler.get_completed_tasks()) == 1

def test_scheduler_get_tasks_by_pet():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    mochi = Pet("Mochi", "Cat")
    bella.add_task(Task("Walk", "7:00 AM", "Daily"))
    mochi.add_task(Task("Feed", "8:00 AM", "Daily"))
    owner.add_pet(bella)
    owner.add_pet(mochi)
    scheduler = Scheduler(owner)
    bella_tasks = scheduler.get_tasks_by_pet("Bella")
    assert len(bella_tasks) == 1
    assert bella_tasks[0][0] == "Bella"

def test_scheduler_sorts_tasks_by_time():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Feed", "8:00 AM", "Daily"))
    bella.add_task(Task("Walk", "7:00 AM", "Daily"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.get_tasks_sorted_by_time()
    assert [task.description for _, task in sorted_tasks] == ["Walk", "Feed"]

def test_scheduler_filters_by_pet_and_status():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    mochi = Pet("Mochi", "Cat")

    done_task = Task("Completed walk", "7:00 AM", "Daily")
    done_task.mark_complete()
    pending_task = Task("Pending feed", "8:00 AM", "Daily")

    bella.add_task(done_task)
    mochi.add_task(pending_task)
    owner.add_pet(bella)
    owner.add_pet(mochi)
    scheduler = Scheduler(owner)

    filtered = scheduler.filter_tasks(pet_name="Mochi", status="pending")
    assert len(filtered) == 1
    assert filtered[0][0] == "Mochi"
    assert filtered[0][1].description == "Pending feed"

def test_scheduler_expands_recurring_tasks():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Daily walk", "7:00 AM", "Daily"))
    bella.add_task(Task("Weekly bath", "10:00 AM", "Weekly"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    expanded = scheduler.expand_recurring_tasks(days=3)
    days_for_daily = [day for day, _, task in expanded if task.description == "Daily walk"]
    days_for_weekly = [day for day, _, task in expanded if task.description == "Weekly bath"]

    assert days_for_daily == [0, 1, 2]
    assert days_for_weekly == [0]

def test_scheduler_detects_conflicts():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Walk", "7:00 AM", "Daily", duration_minutes=45))
    bella.add_task(Task("Feed", "7:20 AM", "Daily", duration_minutes=15))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    first, second = conflicts[0]
    assert first[1].description == "Walk"
    assert second[1].description == "Feed"


# --- detect_same_time_conflicts tests ---

def test_no_same_time_conflicts_when_tasks_differ():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Walk", "7:00 AM", "Daily"))
    bella.add_task(Task("Feed", "8:00 AM", "Daily"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_same_time_conflicts()
    assert conflicts == []

def test_same_pet_same_time_conflict():
    # Two tasks for the same pet at the exact same time
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Walk",  "7:00 AM", "Daily"))
    bella.add_task(Task("Feed",  "7:00 AM", "Daily"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_same_time_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0]["type"] == "same_pet"
    assert conflicts[0]["time"] == "7:00 AM"

def test_cross_pet_same_time_conflict():
    # Two different pets scheduled at the exact same time
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    mochi = Pet("Mochi", "Cat")
    bella.add_task(Task("Walk",     "8:00 AM", "Daily"))
    mochi.add_task(Task("Feed",     "8:00 AM", "Daily"))
    owner.add_pet(bella)
    owner.add_pet(mochi)
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_same_time_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0]["type"] == "cross_pet"
    assert conflicts[0]["time"] == "8:00 AM"
    pet_names = [name for name, _ in conflicts[0]["tasks"]]
    assert "Bella" in pet_names
    assert "Mochi" in pet_names

def test_multiple_same_time_conflicts_detected():
    # Two separate time slots each with a clash
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    mochi = Pet("Mochi", "Cat")
    bella.add_task(Task("Walk",  "7:00 AM", "Daily"))
    mochi.add_task(Task("Feed",  "7:00 AM", "Daily"))   # cross-pet clash at 7
    bella.add_task(Task("Bath",  "10:00 AM", "Daily"))
    mochi.add_task(Task("Nap",   "10:00 AM", "Daily"))  # cross-pet clash at 10
    owner.add_pet(bella)
    owner.add_pet(mochi)
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_same_time_conflicts()
    assert len(conflicts) == 2


# --- next_occurrence / complete_task tests ---

def test_daily_task_next_occurrence_is_tomorrow():
    task = Task("Morning walk", "7:00 AM", "Daily")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=1)

def test_weekly_task_next_occurrence_is_seven_days():
    task = Task("Weekly bath", "10:00 AM", "Weekly")
    next_task = task.next_occurrence()
    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(weeks=1)

def test_once_task_has_no_next_occurrence():
    task = Task("Vet check-up", "9:00 AM", "Once")
    assert task.next_occurrence() is None

def test_next_occurrence_is_pending():
    task = Task("Morning walk", "7:00 AM", "Daily")
    next_task = task.next_occurrence()
    assert next_task.is_complete == False

def test_complete_task_auto_adds_next_to_pet():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    walk = Task("Morning walk", "7:00 AM", "Daily")
    bella.add_task(walk)
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    before_count = len(bella.get_tasks())
    scheduler.complete_task("Bella", walk)
    after_count = len(bella.get_tasks())

    assert walk.is_complete == True
    assert after_count == before_count + 1

def test_complete_once_task_does_not_add_new_task():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    vet = Task("Vet check-up", "9:00 AM", "Once")
    bella.add_task(vet)
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    before_count = len(bella.get_tasks())
    scheduler.complete_task("Bella", vet)
    after_count = len(bella.get_tasks())

    assert vet.is_complete == True
    assert after_count == before_count  # no new task added


# --- Edge case: pets and owners with no tasks ---

def test_pet_with_no_tasks_returns_empty_list():
    pet = Pet("Ghost", "Cat")
    assert pet.get_tasks() == []

def test_owner_with_no_pets_returns_empty_task_list():
    owner = Owner("Sam")
    assert owner.get_all_tasks() == []

def test_scheduler_with_no_tasks_returns_empty_sorted_list():
    owner = Owner("Sam")
    scheduler = Scheduler(owner)
    assert scheduler.get_tasks_sorted_by_time() == []

def test_scheduler_get_tasks_by_nonexistent_pet_returns_empty():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Walk", "7:00 AM", "Daily"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)
    assert scheduler.get_tasks_by_pet("Nonexistent") == []

def test_filter_tasks_nonexistent_pet_returns_empty():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Walk", "7:00 AM", "Daily"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)
    assert scheduler.filter_tasks(pet_name="Nonexistent") == []

def test_filter_tasks_status_case_insensitive():
    # "COMPLETED" and "completed" should both work
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    task = Task("Walk", "7:00 AM", "Daily")
    task.mark_complete()
    bella.add_task(task)
    owner.add_pet(bella)
    scheduler = Scheduler(owner)
    assert len(scheduler.filter_tasks(status="COMPLETED")) == 1
    assert len(scheduler.filter_tasks(status="completed")) == 1

def test_no_tasks_no_conflicts():
    owner = Owner("Alex")
    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []
    assert scheduler.detect_same_time_conflicts() == []
    assert scheduler.check_conflicts() == []


# --- Edge case: time parsing ---

def test_midnight_parses_as_zero_minutes():
    task = Task("Midnight feed", "12:00 AM", "Once")
    assert task.get_time_minutes() == 0

def test_noon_parses_as_720_minutes():
    task = Task("Noon walk", "12:00 PM", "Once")
    assert task.get_time_minutes() == 720

def test_24_hour_format_parses_correctly():
    task = Task("Evening meds", "19:30", "Daily")
    assert task.get_time_minutes() == 19 * 60 + 30

def test_invalid_time_raises_value_error():
    task = Task("Bad time", "not-a-time", "Daily")
    try:
        task.get_time_minutes()
        assert False, "Expected ValueError"
    except ValueError:
        pass

def test_mixed_12h_and_24h_tasks_sort_correctly():
    # "7:00 AM" (420 min) and "19:00" (1140 min) should sort AM first
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Evening meds", "19:00", "Daily"))
    bella.add_task(Task("Morning walk", "7:00 AM", "Daily"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    sorted_tasks = scheduler.get_tasks_sorted_by_time()
    assert sorted_tasks[0][1].description == "Morning walk"
    assert sorted_tasks[1][1].description == "Evening meds"


# --- Edge case: conflict boundaries ---

def test_adjacent_tasks_do_not_conflict():
    # Walk ends at 7:30 AM exactly when Feed starts — should NOT be a conflict
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Walk", "7:00 AM", "Daily", duration_minutes=30))
    bella.add_task(Task("Feed", "7:30 AM", "Daily", duration_minutes=15))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    conflicts = scheduler.detect_conflicts()
    assert conflicts == []

def test_zero_duration_task_does_not_overlap():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Quick check", "8:00 AM", "Daily", duration_minutes=0))
    bella.add_task(Task("Feed", "8:00 AM", "Daily", duration_minutes=15))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    # A task with 0 duration starting at 8:00 ends at 8:00 — no overlap
    conflicts = scheduler.detect_conflicts()
    assert conflicts == []

def test_three_tasks_same_time_all_pairs_reported():
    # Three tasks at the same time for three different pets: 3 pairs expected
    owner = Owner("Alex")
    for name in ("Bella", "Mochi", "Rex"):
        pet = Pet(name, "Dog")
        pet.add_task(Task("Morning feed", "8:00 AM", "Daily"))
        owner.add_pet(pet)
    scheduler = Scheduler(owner)

    same_time = scheduler.detect_same_time_conflicts()
    # All three tasks land in one group; there should be one conflict entry
    assert len(same_time) == 1
    assert same_time[0]["type"] == "cross_pet"
    assert len(same_time[0]["tasks"]) == 3


# --- Edge case: recurring tasks ---

def test_weekly_task_not_on_days_1_through_6():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Weekly bath", "10:00 AM", "Weekly"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    expanded = scheduler.expand_recurring_tasks(days=7)
    days = [day for day, _, _ in expanded]
    # Should only appear on day 0, not days 1-6
    assert days == [0]

def test_expand_recurring_tasks_days_1_only_shows_today():
    # With days=1, a Weekly task should still appear on day 0
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    bella.add_task(Task("Weekly bath", "10:00 AM", "Weekly"))
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    expanded = scheduler.expand_recurring_tasks(days=1)
    assert len(expanded) == 1
    assert expanded[0][0] == 0

def test_next_occurrence_preserves_description_and_time():
    task = Task("Morning walk", "7:00 AM", "Daily", duration_minutes=45)
    next_task = task.next_occurrence()
    assert next_task.description == "Morning walk"
    assert next_task.time == "7:00 AM"
    assert next_task.duration_minutes == 45

def test_complete_task_twice_does_not_crash():
    owner = Owner("Alex")
    bella = Pet("Bella", "Dog")
    walk = Task("Walk", "7:00 AM", "Daily")
    bella.add_task(walk)
    owner.add_pet(bella)
    scheduler = Scheduler(owner)

    scheduler.complete_task("Bella", walk)
    # Completing an already-complete task should not raise
    scheduler.complete_task("Bella", walk)
    assert walk.is_complete == True
