"""
Unit tests for the TodoApp class using pytest.

Tests cover:
- Task creation and storage
- Task listing with filtering
- Marking tasks as complete
- Deleting tasks
- File persistence
- Error handling
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import patch
import sys

# Add the src directory to the path to import the TodoApp
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from todo import TodoApp


@pytest.fixture
def temp_tasks_file(tmp_path):
    """Fixture that provides a temporary tasks file path."""
    tasks_file = tmp_path / "test_tasks.json"
    return str(tasks_file)


@pytest.fixture
def app(temp_tasks_file):
    """Fixture that provides a fresh TodoApp instance with a temporary file."""
    return TodoApp(tasks_file=temp_tasks_file)


@pytest.fixture
def app_with_tasks(temp_tasks_file):
    """Fixture that provides a TodoApp with pre-populated tasks."""
    app = TodoApp(tasks_file=temp_tasks_file)
    app.add_task("Buy groceries", "Milk, eggs, bread")
    app.add_task("Complete project")
    app.add_task("Review pull requests", "Check team PRs")
    return app


class TestTaskCreation:
    """Tests for the add_task method."""

    def test_add_single_task(self, app, capsys):
        """Test adding a single task."""
        app.add_task("Test task")
        assert len(app.tasks) == 1
        assert app.tasks[0]["title"] == "Test task"
        assert app.tasks[0]["completed"] is False
        assert app.tasks[0]["id"] == 1
        captured = capsys.readouterr()
        assert "✓ Task added: Test task" in captured.out

    def test_add_task_with_description(self, app):
        """Test adding a task with a description."""
        app.add_task("Buy groceries", "Milk, eggs, bread")
        assert len(app.tasks) == 1
        assert app.tasks[0]["title"] == "Buy groceries"
        assert app.tasks[0]["description"] == "Milk, eggs, bread"

    def test_add_multiple_tasks(self, app):
        """Test adding multiple tasks and verify ID assignment."""
        app.add_task("First task")
        app.add_task("Second task")
        app.add_task("Third task")
        assert len(app.tasks) == 3
        assert app.tasks[0]["id"] == 1
        assert app.tasks[1]["id"] == 2
        assert app.tasks[2]["id"] == 3

    def test_task_has_created_at_timestamp(self, app):
        """Test that tasks have a created_at timestamp."""
        before = datetime.now()
        app.add_task("Timestamped task")
        after = datetime.now()

        task = app.tasks[0]
        assert "created_at" in task
        created_at = datetime.fromisoformat(task["created_at"])
        assert before <= created_at <= after

    def test_task_default_description_is_empty(self, app):
        """Test that description defaults to empty string."""
        app.add_task("Task without description")
        assert app.tasks[0]["description"] == ""


class TestTaskListing:
    """Tests for the list_tasks method."""

    def test_list_empty_tasks(self, app, capsys):
        """Test listing when no tasks exist."""
        app.list_tasks()
        captured = capsys.readouterr()
        assert "No tasks found." in captured.out

    def test_list_incomplete_tasks(self, app_with_tasks, capsys):
        """Test listing only incomplete tasks."""
        app_with_tasks.list_tasks(show_completed=False)
        captured = capsys.readouterr()
        assert "[1] Buy groceries" in captured.out
        assert "[2] Complete project" in captured.out
        assert "[3] Review pull requests" in captured.out

    def test_list_all_tasks(self, app_with_tasks, capsys):
        """Test listing all tasks including completed ones."""
        app_with_tasks.complete_task(1)
        app_with_tasks.list_tasks(show_completed=True)
        captured = capsys.readouterr()
        assert "[1] Buy groceries" in captured.out
        assert "[2] Complete project" in captured.out

    def test_list_shows_completion_status(self, app_with_tasks, capsys):
        """Test that completed tasks show checkmark and incomplete show circle."""
        app_with_tasks.complete_task(1)
        app_with_tasks.list_tasks(show_completed=True)
        captured = capsys.readouterr()
        output_lines = captured.out.split("\n")
        # Find the line with task 1 and verify it has ✓
        assert any("✓ [1]" in line for line in output_lines)
        # Find the line with task 2 and verify it has ○
        assert any("○ [2]" in line for line in output_lines)

    def test_list_shows_descriptions(self, app_with_tasks, capsys):
        """Test that task descriptions are displayed."""
        app_with_tasks.list_tasks()
        captured = capsys.readouterr()
        assert "Milk, eggs, bread" in captured.out
        assert "Check team PRs" in captured.out

    def test_list_no_incomplete_tasks_with_message(self, app_with_tasks, capsys):
        """Test message when all tasks are complete and show_completed=False."""
        app_with_tasks.complete_task(1)
        app_with_tasks.complete_task(2)
        app_with_tasks.complete_task(3)
        app_with_tasks.list_tasks(show_completed=False)
        captured = capsys.readouterr()
        assert "No incomplete tasks found." in captured.out


class TestCompleteTask:
    """Tests for the complete_task method."""

    def test_complete_existing_task(self, app_with_tasks, capsys):
        """Test completing an existing task."""
        app_with_tasks.complete_task(1)
        assert app_with_tasks.tasks[0]["completed"] is True
        captured = capsys.readouterr()
        assert "✓ Task 1 marked as completed." in captured.out

    def test_complete_task_is_saved(self, app_with_tasks):
        """Test that completing a task persists to file."""
        app_with_tasks.complete_task(1)
        # Reload app from file
        new_app = TodoApp(tasks_file=app_with_tasks.tasks_file)
        assert new_app.tasks[0]["completed"] is True

    def test_complete_nonexistent_task(self, app_with_tasks, capsys):
        """Test completing a task that doesn't exist."""
        app_with_tasks.complete_task(999)
        captured = capsys.readouterr()
        assert "Task 999 not found." in captured.out

    def test_complete_already_completed_task(self, app_with_tasks, capsys):
        """Test completing a task that's already completed."""
        app_with_tasks.complete_task(1)
        app_with_tasks.complete_task(1)
        assert app_with_tasks.tasks[0]["completed"] is True
        captured = capsys.readouterr()
        # Should show two completion messages
        assert captured.out.count("marked as completed") == 2


class TestDeleteTask:
    """Tests for the delete_task method."""

    def test_delete_existing_task(self, app_with_tasks, capsys):
        """Test deleting an existing task."""
        original_count = len(app_with_tasks.tasks)
        app_with_tasks.delete_task(1)
        assert len(app_with_tasks.tasks) == original_count - 1
        captured = capsys.readouterr()
        assert "✓ Task 1 deleted." in captured.out

    def test_delete_task_is_saved(self, app_with_tasks):
        """Test that deleting a task persists to file."""
        app_with_tasks.delete_task(1)
        # Reload app from file
        new_app = TodoApp(tasks_file=app_with_tasks.tasks_file)
        assert len(new_app.tasks) == 2
        assert all(t["id"] != 1 for t in new_app.tasks)

    def test_delete_nonexistent_task(self, app_with_tasks, capsys):
        """Test deleting a task that doesn't exist."""
        original_count = len(app_with_tasks.tasks)
        app_with_tasks.delete_task(999)
        assert len(app_with_tasks.tasks) == original_count
        captured = capsys.readouterr()
        assert "Task 999 not found." in captured.out

    def test_delete_multiple_tasks(self, app_with_tasks):
        """Test deleting multiple tasks in sequence."""
        app_with_tasks.delete_task(1)
        app_with_tasks.delete_task(2)
        assert len(app_with_tasks.tasks) == 1
        assert app_with_tasks.tasks[0]["id"] == 3


class TestFilePersistence:
    """Tests for loading and saving tasks from/to file."""

    def test_tasks_saved_to_file(self, app, temp_tasks_file):
        """Test that tasks are written to the JSON file."""
        app.add_task("Persistent task")
        assert Path(temp_tasks_file).exists()

    def test_tasks_loaded_from_file(self, app, temp_tasks_file):
        """Test that tasks are loaded from an existing file."""
        app.add_task("Task 1")
        app.add_task("Task 2")
        # Create a new app instance to test loading
        new_app = TodoApp(tasks_file=temp_tasks_file)
        assert len(new_app.tasks) == 2
        assert new_app.tasks[0]["title"] == "Task 1"
        assert new_app.tasks[1]["title"] == "Task 2"

    def test_json_file_format(self, app, temp_tasks_file):
        """Test that the file is properly formatted JSON."""
        app.add_task("Check JSON", "Verify format")
        with open(temp_tasks_file, "r") as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["title"] == "Check JSON"

    def test_load_from_nonexistent_file(self):
        """Test that loading from a nonexistent file returns empty list."""
        app = TodoApp(tasks_file="/tmp/nonexistent_file_xyz.json")
        assert app.tasks == []

    def test_json_decode_error_handling(self, app, temp_tasks_file, capsys):
        """Test handling of corrupted JSON file."""
        # Write invalid JSON
        with open(temp_tasks_file, "w") as f:
            f.write("{ invalid json")
        # Reload app - should handle error gracefully
        new_app = TodoApp(tasks_file=temp_tasks_file)
        assert new_app.tasks == []
        captured = capsys.readouterr()
        assert "Error loading tasks" in captured.err


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_task_title(self, app, capsys):
        """Test adding a task with empty title."""
        app.add_task("")
        assert len(app.tasks) == 1
        assert app.tasks[0]["title"] == ""

    def test_task_with_special_characters(self, app):
        """Test adding a task with special characters."""
        special_title = "Buy café items: milk & 🥐"
        app.add_task(special_title)
        assert app.tasks[0]["title"] == special_title

    def test_very_long_description(self, app):
        """Test adding a task with a very long description."""
        long_desc = "x" * 10000
        app.add_task("Long task", long_desc)
        assert app.tasks[0]["description"] == long_desc

    def test_task_id_consistency_after_reload(self, app, temp_tasks_file):
        """Test that task IDs remain consistent after loading from file."""
        app.add_task("Task 1")
        app.add_task("Task 2")
        app.delete_task(1)
        app.add_task("Task 3")
        
        new_app = TodoApp(tasks_file=temp_tasks_file)
        ids = [t["id"] for t in new_app.tasks]
        assert 2 in ids
        assert 3 in ids
        assert 1 not in ids

    def test_negative_task_id(self, app_with_tasks):
        """Test deleting with negative task ID."""
        original_count = len(app_with_tasks.tasks)
        app_with_tasks.delete_task(-1)
        assert len(app_with_tasks.tasks) == original_count

    def test_zero_task_id(self, app_with_tasks):
        """Test deleting with zero task ID."""
        original_count = len(app_with_tasks.tasks)
        app_with_tasks.delete_task(0)
        assert len(app_with_tasks.tasks) == original_count


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_workflow_add_list_complete_delete(self, app, capsys):
        """Test a complete workflow of adding, listing, completing, and deleting."""
        # Add tasks
        app.add_task("First task", "Description 1")
        app.add_task("Second task", "Description 2")
        assert len(app.tasks) == 2

        # List incomplete tasks
        app.list_tasks(show_completed=False)
        captured = capsys.readouterr()
        assert "First task" in captured.out

        # Complete one task
        app.complete_task(1)
        assert app.tasks[0]["completed"] is True

        # List again - should only show second task
        capsys.readouterr()  # Clear previous output
        app.list_tasks(show_completed=False)
        captured = capsys.readouterr()
        assert "Second task" in captured.out
        assert "First task" not in captured.out

        # Delete second task
        app.delete_task(2)
        assert len(app.tasks) == 1

    def test_multiple_apps_same_file(self, temp_tasks_file):
        """Test that multiple app instances can work with the same file."""
        app1 = TodoApp(tasks_file=temp_tasks_file)
        app1.add_task("Task from app1")

        app2 = TodoApp(tasks_file=temp_tasks_file)
        assert len(app2.tasks) == 1
        assert app2.tasks[0]["title"] == "Task from app1"

        app2.add_task("Task from app2")
        app3 = TodoApp(tasks_file=temp_tasks_file)
        assert len(app3.tasks) == 2

    def test_persistence_across_operations(self, app, temp_tasks_file):
        """Test that changes persist across app reloads."""
        app.add_task("Task 1", "Description 1")
        app.add_task("Task 2", "Description 2")
        app.complete_task(1)

        # Reload and verify
        app2 = TodoApp(tasks_file=temp_tasks_file)
        assert len(app2.tasks) == 2
        assert app2.tasks[0]["completed"] is True
        assert app2.tasks[1]["completed"] is False

        # Delete and verify
        app2.delete_task(2)
        app3 = TodoApp(tasks_file=temp_tasks_file)
        assert len(app3.tasks) == 1
        assert app3.tasks[0]["id"] == 1
