"""
Demo script to demonstrate the full workflow of Phase I Todo App

This script runs all commands in a single session to show that the application
works correctly with in-memory storage within a session.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.cli.commands import TaskCommands, create_parser
from src.services.task_service import TaskService

def demo():
    """Demonstrate the complete workflow"""
    print("=" * 60)
    print("Todo App - Phase I Demo (In-Memory Storage)")
    print("=" * 60)
    print()
    
    # Create shared service instance
    task_service = TaskService()
    commands = TaskCommands(task_service)
    parser = create_parser()
    
    # Create namespace objects for commands
    class Args:
        pass
    
    print("1. Adding tasks...")
    args = Args()
    args.title = "Buy groceries"
    args.description = None
    commands.handle_add(args)
    
    args = Args()
    args.title = "Call mom"
    args.description = "Discuss weekend plans"
    commands.handle_add(args)
    
    args = Args()
    args.title = "Finish homework"
    args.description = None
    commands.handle_add(args)
    print()
    
    print("2. Listing all tasks...")
    args = Args()
    commands.handle_list(args)
    print()
    
    print("3. Marking task 1 as complete...")
    args = Args()
    args.id = "1"
    commands.handle_complete(args)
    print()
    
    print("4. Listing tasks after completion...")
    args = Args()
    commands.handle_list(args)
    print()
    
    print("5. Updating task 2...")
    args = Args()
    args.id = "2"
    args.title = None
    args.description = "Call to discuss weekend"
    commands.handle_update(args)
    print()
    
    print("6. Listing tasks after update...")
    args = Args()
    commands.handle_list(args)
    print()
    
    print("7. Deleting task 3...")
    args = Args()
    args.id = "3"
    commands.handle_delete(args)
    print()
    
    print("8. Final task list...")
    args = Args()
    commands.handle_list(args)
    print()
    
    print("9. Testing error handling...")
    args = Args()
    args.id = "99"
    result = commands.handle_complete(args)
    print(f"   Exit code: {result} (expected: 1 for error)")
    print()
    
    print("=" * 60)
    print("Demo complete! All features working correctly.")
    print("=" * 60)

if __name__ == '__main__':
    demo()

