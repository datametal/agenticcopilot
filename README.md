# Agentic Copilot - To-Do List CLI

A simple command-line to-do list application built with Python, featuring persistent task storage using JSON.

## Overview

This project demonstrates a practical Python CLI application that manages personal tasks with the following features:

- **Add tasks** with titles and optional descriptions
- **List tasks** with filtering options
- **Mark tasks as completed**
- **Delete tasks**
- **Persistent storage** using JSON format
- **Command-line interface** using argparse

## Project Structure

```
agenticcopilot/
├── src/
│   └── todo.py           # Main CLI application
├── tasks.json            # Task storage (auto-created)
├── requirements.txt      # Project dependencies
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.7 or higher

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd agenticcopilot
```

2. (Optional) Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Commands

#### Add a Task
```bash
python src/todo.py add "Buy groceries"
python src/todo.py add "Complete project" -d "Due tomorrow"
```

#### List Tasks
```bash
# Show only incomplete tasks
python src/todo.py list

# Show all tasks including completed ones
python src/todo.py list --all
```

#### Complete a Task
```bash
python src/todo.py complete 1
```

#### Delete a Task
```bash
python src/todo.py delete 1
```

### Custom Tasks File

You can specify a custom location for the tasks file:
```bash
python src/todo.py --tasks-file /path/to/tasks.json list
```

## Task Storage

Tasks are stored in JSON format with the following structure:

```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread, and vegetables",
  "completed": false,
  "created_at": "2026-02-09T10:00:00"
}
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

Format code with Black:
```bash
black src/
```

Check with Flake8:
```bash
flake8 src/
```

Type checking with mypy:
```bash
mypy src/
```

## Features

- ✅ Simple and intuitive command-line interface
- ✅ Persistent task storage with JSON
- ✅ Task descriptions and metadata
- ✅ Timestamp tracking for created tasks
- ✅ Status tracking (completed/incomplete)
- ✅ Error handling and user-friendly messages

## Future Enhancements

- Task prioritization (high, medium, low)
- Due dates and reminders
- Task categories/tags
- Search and filter functionality
- Data export (CSV, etc.)
- Web interface using Flask/FastAPI
- Database support (SQLite, PostgreSQL)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
