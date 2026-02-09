#!/usr/bin/env python3
"""
Simple To-Do List CLI Application

A command-line tool for managing tasks with persistent JSON storage.
Supports adding, listing, and completing tasks.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class TodoApp:
    """A simple to-do list application using JSON for task storage."""

    def __init__(self, tasks_file: str = "tasks.json"):
        """
        Initialize the TodoApp.

        Args:
            tasks_file: Path to the JSON file for storing tasks.
        """
        self.tasks_file = Path(tasks_file)
        self.tasks: List[Dict[str, Any]] = self._load_tasks()

    def _load_tasks(self) -> List[Dict[str, Any]]:
        """
        Load tasks from the JSON file.

        Returns:
            List of task dictionaries, or empty list if file doesn't exist.
        """
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading tasks: {e}", file=sys.stderr)
                return []
        return []

    def _save_tasks(self) -> None:
        """Save tasks to the JSON file."""
        try:
            with open(self.tasks_file, "w") as f:
                json.dump(self.tasks, f, indent=2)
        except IOError as e:
            print(f"Error saving tasks: {e}", file=sys.stderr)
            sys.exit(1)

    def add_task(self, title: str, description: str = "") -> None:
        """
        Add a new task to the to-do list.

        Args:
            title: The task title.
            description: Optional task description.
        """
        # Generate ID based on max existing ID to handle deleted tasks
        next_id = max((t["id"] for t in self.tasks), default=0) + 1
        task = {
            "id": next_id,
            "title": title,
            "description": description,
            "completed": False,
            "created_at": datetime.now().isoformat(),
        }
        self.tasks.append(task)
        self._save_tasks()
        print(f"✓ Task added: {title}")

    def list_tasks(self, show_completed: bool = False) -> None:
        """
        List all tasks.

        Args:
            show_completed: If True, show completed tasks. If False, show only incomplete.
        """
        if not self.tasks:
            print("No tasks found.")
            return

        tasks_to_show = self.tasks
        if not show_completed:
            tasks_to_show = [t for t in self.tasks if not t.get("completed", False)]

        if not tasks_to_show:
            print("No incomplete tasks found.")
            return

        print("\n📋 To-Do List:")
        print("-" * 60)
        for task in tasks_to_show:
            status = "✓" if task.get("completed", False) else "○"
            print(f"{status} [{task['id']}] {task['title']}")
            if task.get("description"):
                print(f"    └─ {task['description']}")
        print("-" * 60)

    def complete_task(self, task_id: int) -> None:
        """
        Mark a task as completed.

        Args:
            task_id: The ID of the task to complete.
        """
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                self._save_tasks()
                print(f"✓ Task {task_id} marked as completed.")
                return
        print(f"Task {task_id} not found.")

    def delete_task(self, task_id: int) -> None:
        """
        Delete a task from the list.

        Args:
            task_id: The ID of the task to delete.
        """
        original_length = len(self.tasks)
        self.tasks = [t for t in self.tasks if t["id"] != task_id]

        if len(self.tasks) < original_length:
            self._save_tasks()
            print(f"✓ Task {task_id} deleted.")
        else:
            print(f"Task {task_id} not found.")


def main() -> None:
    """Main entry point for the CLI application."""
    parser = argparse.ArgumentParser(
        description="A simple to-do list manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s add "Buy groceries"
  %(prog)s add "Complete project" -d "Due tomorrow"
  %(prog)s list
  %(prog)s list --all
  %(prog)s complete 1
  %(prog)s delete 1
        """,
    )

    parser.add_argument(
        "--tasks-file",
        default="tasks.json",
        help="Path to the tasks JSON file (default: tasks.json)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument(
        "-d", "--description", default="", help="Task description"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument(
        "--all", action="store_true", help="Show all tasks including completed ones"
    )

    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark a task as completed")
    complete_parser.add_argument("id", type=int, help="Task ID")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task ID")

    args = parser.parse_args()

    # Initialize the app
    app = TodoApp(tasks_file=args.tasks_file)

    # Handle commands
    if args.command == "add":
        app.add_task(args.title, args.description)
    elif args.command == "list":
        app.list_tasks(show_completed=args.all)
    elif args.command == "complete":
        app.complete_task(args.id)
    elif args.command == "delete":
        app.delete_task(args.id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
