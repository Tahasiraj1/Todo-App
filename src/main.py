"""
Main entry point for Phase I - Todo Console App

[Task]: T039 [From]: plan.md §Project Structure, contracts/cli-commands.md

Note: Each command invocation is a separate process. Tasks are stored in-memory
and do not persist between separate command calls. This is expected behavior
for Phase I (in-memory storage only).
"""

import sys
import argparse
import shlex
from pathlib import Path

# Add project root to Python path to enable imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.cli.commands import TaskCommands, create_parser
from src.services.task_service import TaskService


def main() -> int:
    """
    Main entry point for the todo application.
    
    Sets up argparse, registers all commands, and handles command routing.
    Supports both single-command mode and interactive mode.
    
    [Task]: T039 [From]: plan.md §Project Structure, contracts/cli-commands.md §General Command Behavior
    
    Interactive Mode: If no command is provided, enters interactive mode where
    tasks persist in-memory for the session, allowing full workflow testing.
    
    Single Command Mode: If a command is provided, executes and exits.
    Note: In single-command mode, each invocation is a separate process with
    fresh in-memory storage. Use interactive mode for testing full workflows.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = create_parser()
    
    # If no arguments provided, enter interactive mode
    if len(sys.argv) == 1:
        task_service = TaskService()
        commands = TaskCommands(task_service)
        return _interactive_mode(commands, parser)
    
    args = parser.parse_args()
    
    # Initialize task service (in-memory storage)
    task_service = TaskService()
    commands = TaskCommands(task_service)
    
    # Route to appropriate command handler
    if args.command == 'add':
        return commands.handle_add(args)
    elif args.command == 'list':
        return commands.handle_list(args)
    elif args.command == 'complete':
        return commands.handle_complete(args)
    elif args.command == 'update':
        return commands.handle_update(args)
    elif args.command == 'delete':
        return commands.handle_delete(args)
    else:
        parser.print_help()
        return 1


def _interactive_mode(commands: TaskCommands, parser: argparse.ArgumentParser) -> int:
    """
    Interactive mode for testing and demonstrating the full workflow.
    
    Tasks persist in-memory for the duration of the interactive session,
    allowing users to test the complete workflow: add → list → complete → update → delete.
    
    This mode enables testing all features as required by the hackathon specification.
    """
    print("Todo App - Interactive Mode")
    print("Type 'help' for commands, 'exit' or 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("todo> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                return 0
            
            if user_input.lower() in ['help', 'h', '?']:
                print("\nAvailable commands:")
                print("  add <title> [description]     - Create a new task")
                print("  list                           - View all tasks")
                print("  complete <id>                  - Mark task as complete/incomplete")
                print("  update <id> [--title T] [--description D] - Update task")
                print("  delete <id>                    - Delete a task")
                print("  help                           - Show this help")
                print("  exit/quit/q                    - Exit interactive mode")
                print()
                continue
            
            # Parse and execute command
            try:
                # Use shlex to properly handle quoted arguments
                try:
                    parsed_args = shlex.split(user_input)
                except ValueError as e:
                    print(f"Error parsing command: {str(e)}", file=sys.stderr)
                    continue
                
                if not parsed_args:
                    continue
                
                # Temporarily replace sys.argv for argparse
                original_argv = sys.argv
                sys.argv = ['todo'] + parsed_args
                
                try:
                    args = parser.parse_args()
                    
                    if args.command == 'add':
                        commands.handle_add(args)
                    elif args.command == 'list':
                        commands.handle_list(args)
                    elif args.command == 'complete':
                        commands.handle_complete(args)
                    elif args.command == 'update':
                        commands.handle_update(args)
                    elif args.command == 'delete':
                        commands.handle_delete(args)
                    else:
                        print("Unknown command. Type 'help' for available commands.")
                finally:
                    sys.argv = original_argv
                    
            except SystemExit:
                # argparse calls sys.exit() on help or errors, catch it
                pass
            except Exception as e:
                print(f"Error: {str(e)}", file=sys.stderr)
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            return 0
        except EOFError:
            print("\nGoodbye!")
            return 0


if __name__ == '__main__':
    sys.exit(main())
