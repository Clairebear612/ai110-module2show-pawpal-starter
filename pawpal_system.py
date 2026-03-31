class Task:
    def __init__(self, description, time, frequency):
        self.description = description
        self.time = time
        self.frequency = frequency
        self.is_complete = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_complete = True

    def mark_incomplete(self):
        """Mark this task as not yet completed."""
        self.is_complete = False


class Pet:
    def __init__(self, name, species):
        self.name = name
        self.species = species
        self.__tasks = []

    def add_task(self, task):
        """Add a task to this pet's task list."""
        self.__tasks.append(task)

    def remove_task(self, task):
        """Remove a task from this pet's task list."""
        self.__tasks.remove(task)

    def get_tasks(self):
        """Return all tasks assigned to this pet."""
        return self.__tasks


class Owner:
    def __init__(self, name):
        self.name = name
        self.__pets = []

    def add_pet(self, pet):
        """Add a pet to this owner's pet list."""
        self.__pets.append(pet)

    def remove_pet(self, pet):
        """Remove a pet from this owner's pet list."""
        self.__pets.remove(pet)

    def get_pets(self):
        """Return all pets belonging to this owner."""
        return self.__pets

    def get_all_tasks(self):
        """Return all tasks across all pets as (pet_name, task) tuples."""
        all_tasks = []
        for pet in self.__pets:
            for task in pet.get_tasks():
                all_tasks.append((pet.name, task))
        return all_tasks


class Scheduler:
    def __init__(self, owner):
        self.__owner = owner

    def get_all_tasks(self):
        """Return all tasks for all pets owned by this scheduler's owner."""
        return self.__owner.get_all_tasks()

    def get_tasks_by_pet(self, pet_name):
        """Return all tasks for a specific pet by name."""
        return [
            (name, task)
            for name, task in self.__owner.get_all_tasks()
            if name == pet_name
        ]

    def get_pending_tasks(self):
        """Return all tasks that have not yet been completed."""
        return [
            (name, task)
            for name, task in self.__owner.get_all_tasks()
            if not task.is_complete
        ]

    def get_completed_tasks(self):
        """Return all tasks that have been marked as completed."""
        return [
            (name, task)
            for name, task in self.__owner.get_all_tasks()
            if task.is_complete
        ]
