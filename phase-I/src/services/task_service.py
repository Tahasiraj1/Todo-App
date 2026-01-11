"""
Task service for Phase I - Todo Console App

[Task]: T007, T008, T009, T010, T014, T019, T020, T025, T026, T027, T033, T034
[From]: spec.md §Requirements, plan.md §Project Structure, data-model.md §Data Storage
"""

from typing import List, Optional
from src.models.task import Task


class TaskNotFoundError(Exception):
    """Raised when a task with the given ID is not found."""
    pass


class TaskService:
    """
    Service for managing tasks in memory.
    
    Provides business logic for task operations: create, read, update, delete, complete.
    """
    
    def __init__(self):
        """
        Initialize the task service with empty in-memory storage.
        
        [Task]: T007 [From]: plan.md §Project Structure, data-model.md §Data Storage
        """
        self._tasks: List[Task] = []
        self._next_id: int = 1
    
    def _generate_id(self) -> int:
        """
        Generate the next sequential task ID.
        
        [Task]: T008 [From]: data-model.md §Entities, research.md §Task ID Generation
        
        Returns:
            Next sequential integer ID starting from 1
        """
        task_id = self._next_id
        self._next_id += 1
        return task_id
    
    def add_task(self, title: str, description: Optional[str] = None) -> Task:
        """
        Create a new task with a title and optional description.
        
        [Task]: T009 [From]: spec.md §FR-001, FR-002, FR-003, contracts/cli-commands.md §Add Task
        
        Args:
            title: Task title (required, non-empty)
            description: Optional task description
            
        Returns:
            Created Task instance with assigned ID
            
        Raises:
            ValueError: If title is empty or None
        """
        # Validation is handled by Task.__init__, but we check here for clarity
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        
        task_id = self._generate_id()
        task = Task(
            id=task_id,
            title=title,
            description=description,
            completed=False
        )
        self._tasks.append(task)
        return task
    
    def get_all_tasks(self) -> List[Task]:
        """
        Retrieve all tasks from storage.
        
        [Task]: T014 [From]: spec.md §FR-004, contracts/cli-commands.md §List Tasks
        
        Returns:
            List of all Task instances
        """
        return self._tasks.copy()
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """
        Find a task by its ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task instance if found, None otherwise
        """
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None
    
    def toggle_complete(self, task_id: int) -> Task:
        """
        Toggle task completion status.
        
        [Task]: T019 [From]: spec.md §FR-005, contracts/cli-commands.md §Mark Complete
        
        Args:
            task_id: Task identifier
            
        Returns:
            Updated Task instance
            
        Raises:
            TaskNotFoundError: If task with given ID does not exist
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        
        task.completed = not task.completed
        return task
    
    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Task:
        """
        Update task title and/or description.
        
        [Task]: T025 [From]: spec.md §FR-006, FR-007, contracts/cli-commands.md §Update Task
        
        Args:
            task_id: Task identifier
            title: New task title (optional)
            description: New task description (optional)
            
        Returns:
            Updated Task instance
            
        Raises:
            TaskNotFoundError: If task with given ID does not exist
            ValueError: If no fields provided or title is empty
        """
        if title is None and description is None:
            raise ValueError("At least one field (title or description) must be provided")
        
        task = self.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        
        if title is not None:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            task.title = title.strip()
        
        if description is not None:
            task.description = description.strip() if description.strip() else None
        
        return task
    
    def delete_task(self, task_id: int) -> Task:
        """
        Remove a task from storage.
        
        [Task]: T033 [From]: spec.md §FR-008, contracts/cli-commands.md §Delete Task
        
        Args:
            task_id: Task identifier
            
        Returns:
            Deleted Task instance
            
        Raises:
            TaskNotFoundError: If task with given ID does not exist
        """
        task = self.get_task_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with ID {task_id} not found")
        
        self._tasks.remove(task)
        return task

