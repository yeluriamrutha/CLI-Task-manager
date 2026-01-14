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



