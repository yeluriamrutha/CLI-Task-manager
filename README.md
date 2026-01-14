\# Task Manager

┌────────────┐
│    CLI     │
│  (Click)   │
└─────┬──────┘
      │
      ▼
┌────────────┐
│  Commands  │  ← Create / Update / Delete / Complete
│ (Undoable) │
└─────┬──────┘
      │
      ▼
┌────────────┐
│UndoManager │  ← Undo / Redo stacks
└─────┬──────┘
      │
      ▼
┌────────────┐
│ TaskManager│  ← Business rules
└─────┬──────┘
      │
      ▼
┌────────────┐
│  Storage   │  ← SQLite / InMemory
└────────────┘



Simple Task / Project Management CLI.



Day 1: Project scaffold, models, and tests.

## Resume Highlights

- Designed a Python CLI application using layered architecture
- Implemented undo/redo functionality using the Command pattern
- Added SQLite persistence with clean separation of concerns
- Wrote unit tests to ensure business logic correctness
- Managed feature development using Git branches and commits


