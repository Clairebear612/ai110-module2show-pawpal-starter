from datetime import datetime, timedelta


class Task:
    """Represents a single pet care activity with a scheduled time and recurrence.

    Attributes:
        description (str): Human-readable name of the task (e.g. "Morning walk").
        time (str): Scheduled start time as a string (e.g. "7:00 AM" or "14:00").
        frequency (str): Recurrence rule — "Daily", "Weekly", or "Once".
        duration_minutes (int): How long the task takes. Used for overlap detection.
        is_complete (bool): Whether the task has been marked done. Starts as False.
    """

    def __init__(self, description, time, frequency, duration_minutes=30):
        """Initialize a Task.

        Args:
            description (str): Name of the activity.
            time (str): Start time string in "HH:MM AM/PM" or "HH:MM" format.
            frequency (str): "Daily", "Weekly", or "Once".
            duration_minutes (int): Duration in minutes. Defaults to 30.
        """
        self.description = description
        self.time = time
        self.frequency = frequency
        self.duration_minutes = duration_minutes
        self.is_complete = False

    def get_time_minutes(self):
        """Convert the task's time string to minutes since midnight.

        Supports both 12-hour ("7:00 AM") and 24-hour ("19:00") formats.
        Used as the sort key when ordering tasks chronologically.

        Returns:
            int: Minutes since midnight (e.g. "7:00 AM" -> 420).

        Raises:
            ValueError: If the time string does not match any supported format.
        """
        time_formats = ["%I:%M %p", "%H:%M"]
        for time_format in time_formats:
            try:
                parsed = datetime.strptime(self.time.strip(), time_format)
                return parsed.hour * 60 + parsed.minute
            except ValueError:
                continue
        raise ValueError(f"Unsupported time format: {self.time}")

    def occurs_on_day(self, day_offset):
        """Determine whether this task should appear on a given schedule day.

        Args:
            day_offset (int): Days from today (0 = today, 1 = tomorrow, etc.).

        Returns:
            bool: True if the task should run on this day based on its frequency.
                  Daily tasks always return True. Weekly tasks return True every
                  7th day. Once tasks only return True on day 0.
        """
        frequency = self.frequency.strip().lower()
        if frequency == "daily":
            return True
        if frequency == "weekly":
            return day_offset % 7 == 0
        return day_offset == 0

    def next_occurrence(self):
        """Create a new pending Task scheduled for the next occurrence.

        Calculates the next due date using timedelta based on frequency:
        - "Daily"  -> today + 1 day
        - "Weekly" -> today + 7 days
        - "Once"   -> returns None (task does not repeat)

        Returns:
            Task: A fresh, incomplete Task with a due_date attribute set,
                  or None if the frequency is "Once".
        """
        frequency = self.frequency.strip().lower()
        if frequency == "daily":
            delta = timedelta(days=1)
        elif frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        next_task = Task(self.description, self.time, self.frequency, self.duration_minutes)
        next_task.due_date = datetime.today().date() + delta
        return next_task

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

    def filter_tasks(self, pet_name=None, status=None):
        """Return tasks filtered by optional pet name and/or completion status.

        Both filters are optional and stack — if both are provided, only tasks
        matching the pet name AND the status are returned.

        Args:
            pet_name (str, optional): Only return tasks belonging to this pet.
            status (str, optional): "pending" returns incomplete tasks;
                                    "completed" returns finished tasks.
                                    Case-insensitive. Defaults to None (no filter).

        Returns:
            list[tuple[str, Task]]: Filtered list of (pet_name, task) tuples.
        """
        tasks = self.__owner.get_all_tasks()

        if pet_name is not None:
            tasks = [(name, task) for name, task in tasks if name == pet_name]

        if status is not None:
            normalized_status = status.strip().lower()
            if normalized_status == "pending":
                tasks = [(name, task) for name, task in tasks if not task.is_complete]
            elif normalized_status == "completed":
                tasks = [(name, task) for name, task in tasks if task.is_complete]

        return tasks

    def get_tasks_sorted_by_time(self, pet_name=None, status=None):
        """Return filtered tasks sorted chronologically by start time.

        Applies filter_tasks() first, then sorts using each Task's
        get_time_minutes() value as the sort key.

        Args:
            pet_name (str, optional): Limit results to this pet. Defaults to None.
            status (str, optional): "pending" or "completed". Defaults to None.

        Returns:
            list[tuple[str, Task]]: Sorted (pet_name, task) tuples, earliest first.
        """
        tasks = self.filter_tasks(pet_name=pet_name, status=status)
        return sorted(tasks, key=lambda pair: pair[1].get_time_minutes())

    def expand_recurring_tasks(self, days=7, pet_name=None, status=None):
        """Expand recurring tasks into a multi-day schedule.

        Iterates over a range of days and includes each task on the days
        it is scheduled to occur, based on Task.occurs_on_day(). Tasks
        within each day are sorted by start time.

        Args:
            days (int): Number of days to expand. Defaults to 7.
            pet_name (str, optional): Limit to this pet's tasks. Defaults to None.
            status (str, optional): "pending" or "completed". Defaults to None.

        Returns:
            list[tuple[int, str, Task]]: Entries as (day_offset, pet_name, task),
                                         sorted by day then by time within each day.
        """
        base_tasks = self.filter_tasks(pet_name=pet_name, status=status)
        expanded = []

        for day_offset in range(days):
            day_tasks = [
                (day_offset, name, task)
                for name, task in base_tasks
                if task.occurs_on_day(day_offset)
            ]
            day_tasks.sort(key=lambda row: row[2].get_time_minutes())
            expanded.extend(day_tasks)

        return expanded

    def detect_conflicts(self, day_offset=0, pet_name=None):
        """Detect tasks whose time windows overlap on a given day.

        Uses a sweep-line approach: tasks are sorted by start time, then each
        task is compared against the next to check if the second starts before
        the first ends (start + duration_minutes).

        Args:
            day_offset (int): Day to check (0 = today). Defaults to 0.
            pet_name (str, optional): Limit check to one pet. Defaults to None.

        Returns:
            list[tuple]: Each entry is ((pet_a, task_a), (pet_b, task_b))
                         where the two tasks overlap in time.
        """
        day_tasks = [
            (name, task)
            for current_day, name, task in self.expand_recurring_tasks(
                days=day_offset + 1,
                pet_name=pet_name,
            )
            if current_day == day_offset
        ]

        sorted_tasks = sorted(day_tasks, key=lambda pair: pair[1].get_time_minutes())
        conflicts = []

        for index, (first_pet, first_task) in enumerate(sorted_tasks):
            first_start = first_task.get_time_minutes()
            first_end = first_start + first_task.duration_minutes

            for second_pet, second_task in sorted_tasks[index + 1:]:
                second_start = second_task.get_time_minutes()
                if second_start >= first_end:
                    break
                conflicts.append(((first_pet, first_task), (second_pet, second_task)))

        return conflicts

    def detect_same_time_conflicts(self, day_offset=0):
        """
        Return conflicts where two or more tasks share the exact same start time.
        Works across all pets (cross-pet) and within the same pet.
        Returns a list of dicts with keys: 'time', 'type', 'tasks'.
          - 'type' is 'same_pet' or 'cross_pet'
          - 'tasks' is a list of (pet_name, task) tuples at that time
        """
        from collections import defaultdict

        day_tasks = [
            (name, task)
            for current_day, name, task in self.expand_recurring_tasks(days=day_offset + 1)
            if current_day == day_offset
        ]

        # Group all tasks by their exact time string
        time_map = defaultdict(list)
        for pet_name, task in day_tasks:
            time_map[task.time].append((pet_name, task))

        conflicts = []
        for time, group in time_map.items():
            if len(group) < 2:
                continue
            pet_names = [name for name, _ in group]
            conflict_type = "same_pet" if len(set(pet_names)) == 1 else "cross_pet"
            conflicts.append({
                "time": time,
                "type": conflict_type,
                "tasks": group,
            })

        return conflicts

    def check_conflicts(self, day_offset=0):
        """
        Lightweight conflict check that always returns a list of warning strings.
        Never raises — any internal error is caught and reported as a warning.
        Combines overlap detection and exact same-time detection.
        """
        warnings = []

        try:
            for (pet_a, task_a), (pet_b, task_b) in self.detect_conflicts(day_offset=day_offset):
                warnings.append(
                    f"WARNING: '{task_a.description}' ({pet_a}, {task_a.time}, "
                    f"{task_a.duration_minutes}min) overlaps "
                    f"'{task_b.description}' ({pet_b}, {task_b.time})"
                )
        except Exception as e:
            warnings.append(f"WARNING: Could not check overlap conflicts — {e}")

        try:
            for conflict in self.detect_same_time_conflicts(day_offset=day_offset):
                names = ", ".join(
                    f"{name} → '{task.description}'"
                    for name, task in conflict["tasks"]
                )
                warnings.append(
                    f"WARNING: [{conflict['type']}] Same start time {conflict['time']}: {names}"
                )
        except Exception as e:
            warnings.append(f"WARNING: Could not check same-time conflicts — {e}")

        return warnings

    def complete_task(self, pet_name, task):
        """Mark a task complete and auto-schedule its next occurrence if recurring.

        Calls task.mark_complete(), then task.next_occurrence(). If a next
        occurrence exists, it is appended to the matching pet's task list.

        Args:
            pet_name (str): Name of the pet the task belongs to.
            task (Task): The task to mark complete.

        Returns:
            Task: The newly created next-occurrence Task, or None if the task
                  does not recur ("Once" frequency).
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            for pet in self.__owner.get_pets():
                if pet.name == pet_name:
                    pet.add_task(next_task)
                    return next_task
        return None

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
