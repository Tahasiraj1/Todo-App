"""
CLI command handlers for Phase I - Todo Console App

[Task]: T011, T012, T013, T015, T016, T017, T018, T021, T022, T023, T024, T028, T029, T030, T031, T032, T035, T036, T037, T038, T040, T041, T042
[From]: spec.md §User Stories, contracts/cli-commands.md, plan.md §Project Structure
"""

import sys
import argparse
from typing import Optional
from src.services.task_service import TaskService, TaskNotFoundError


class TaskCommands:
    """
    Command-line interface handlers for task operations.
    """
    
    def __init__(self, task_service: TaskService):
        """
        Initialize CLI commands with task service.
        
        Args:
            task_service: TaskService instance for business logic
        """
        self.task_service = task_service
    
    def handle_add(self, args: argparse.Namespace) -> int:
        """
        Handle 'add' command - Create a new task.
        
        [Task]: T011, T012, T013 [From]: spec.md §US1, contracts/cli-commands.md §Add Task
        
        Args:
            args: Parsed arguments containing title and optional description
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        title = args.title
        description = args.description if hasattr(args, 'description') else None
        
        try:
            task = self.task_service.add_task(title, description)
            print(f"Task added: ID {task.id} - {task.title}", file=sys.stdout)
            return 0
        except ValueError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
    
    def handle_list(self, args: argparse.Namespace) -> int:
        """
        Handle 'list' command - Display all tasks.
        
        [Task]: T015, T016, T017, T018 [From]: spec.md §US2, contracts/cli-commands.md §List Tasks
        
        Args:
            args: Parsed arguments (no arguments for list command)
            
        Returns:
            Exit code (0 for success)
        """
        tasks = self.task_service.get_all_tasks()
        
        if not tasks:
            print("No tasks found. Use 'add' to create a task.", file=sys.stdout)
            return 0
        
        print("Tasks:", file=sys.stdout)
        for task in tasks:
            status = "[X]" if task.completed else "[ ]"
            print(f"  {task.id}. {status} {task.title}", file=sys.stdout)
            if task.description:
                print(f"      Description: {task.description}", file=sys.stdout)
        
        completed_count = sum(1 for task in tasks if task.completed)
        pending_count = len(tasks) - completed_count
        print(f"\nTotal: {len(tasks)} tasks ({completed_count} completed, {pending_count} pending)", file=sys.stdout)
        return 0
    
    def handle_complete(self, args: argparse.Namespace) -> int:
        """
        Handle 'complete' command - Toggle task completion status.
        
        [Task]: T021, T022, T023, T024 [From]: spec.md §US3, contracts/cli-commands.md §Mark Complete
        
        Args:
            args: Parsed arguments containing task ID
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            task_id = int(args.id)
        except (ValueError, TypeError):
            print("Error: Invalid task ID. Must be a number.", file=sys.stderr)
            return 1
        
        try:
            task = self.task_service.toggle_complete(task_id)
            status = "complete" if task.completed else "incomplete"
            print(f"Task {task_id} marked as {status}.", file=sys.stdout)
            return 0
        except TaskNotFoundError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
    
    def handle_update(self, args: argparse.Namespace) -> int:
        """
        Handle 'update' command - Update task title and/or description.
        
        [Task]: T028, T029, T030, T031, T032 [From]: spec.md §US4, contracts/cli-commands.md §Update Task
        
        Args:
            args: Parsed arguments containing task ID and optional --title, --description
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            task_id = int(args.id)
        except (ValueError, TypeError):
            print("Error: Invalid task ID. Must be a number.", file=sys.stderr)
            return 1
        
        title = getattr(args, 'title', None)
        description = getattr(args, 'description', None)
        
        try:
            task = self.task_service.update_task(task_id, title=title, description=description)
            print(f"Task {task_id} updated successfully.", file=sys.stdout)
            return 0
        except TaskNotFoundError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
        except ValueError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1
    
    def handle_delete(self, args: argparse.Namespace) -> int:
        """
        Handle 'delete' command - Remove a task.
        
        [Task]: T035, T036, T037, T038 [From]: spec.md §US5, contracts/cli-commands.md §Delete Task
        
        Args:
            args: Parsed arguments containing task ID
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            task_id = int(args.id)
        except (ValueError, TypeError):
            print("Error: Invalid task ID. Must be a number.", file=sys.stderr)
            return 1
        
        try:
            self.task_service.delete_task(task_id)
            print(f"Task {task_id} deleted successfully.", file=sys.stdout)
            return 0
        except TaskNotFoundError as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            return 1


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser for CLI commands.
    
    [Task]: T039, T040 [From]: contracts/cli-commands.md, plan.md §Project Structure
    """
    parser = argparse.ArgumentParser(
        prog='todo',
        description='Todo App - Phase I Console Application',
        add_help=False  # We'll handle help manually in interactive mode
    )
    
    parser.add_argument('-h', '--help', action='help', help='Show help message')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands', metavar='COMMAND')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Create a new task')
    add_parser.add_argument('title', help='Task title (required)')
    add_parser.add_argument('description', nargs='?', help='Task description (optional)')
    
    # List command
    subparsers.add_parser('list', help='View all tasks')
    
    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark a task as complete/incomplete')
    complete_parser.add_argument('id', help='Task ID to mark complete')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update task title or description')
    update_parser.add_argument('id', help='Task ID to update')
    update_parser.add_argument('--title', help='New task title')
    update_parser.add_argument('--description', help='New task description')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Remove a task')
    delete_parser.add_argument('id', help='Task ID to delete')
    
    return parser

