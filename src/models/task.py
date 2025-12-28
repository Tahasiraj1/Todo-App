"""
Task data model for Phase I - Todo Console App

[Task]: T006 [From]: spec.md §Key Entities, plan.md §Project Structure, data-model.md §Entities
"""

from datetime import datetime
from typing import Optional


class Task:
    """
    Represents a single todo item stored in memory.
    
    Attributes:
        id: Unique identifier (integer, auto-generated)
        title: Task title (string, required, non-empty)
        description: Task description (string, optional)
        completed: Completion status (boolean, default: False)
        created_at: Timestamp when task was created (optional)
    """
    
    def __init__(
        self,
        id: int,
        title: str,
        description: Optional[str] = None,
        completed: bool = False,
        created_at: Optional[datetime] = None
    ):
        """
        Initialize a Task instance.
        
        Args:
            id: Unique identifier for the task
            title: Task title (must be non-empty)
            description: Optional task description
            completed: Completion status (default: False)
            created_at: Optional creation timestamp (default: current time)
        """
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        
        self.id = id
        self.title = title.strip()
        self.description = description.strip() if description else None
        self.completed = completed
        self.created_at = created_at if created_at else datetime.now()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self) -> str:
        """String representation of the task."""
        status = "[X]" if self.completed else "[ ]"
        return f"{self.id}. {status} {self.title}"

