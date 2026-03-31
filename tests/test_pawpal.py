import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
