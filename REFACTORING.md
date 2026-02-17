# NmapDojo Refactoring Documentation

## Overview

The NmapDojo application has been refactored from a single 1159-line `main.py` file into a modular architecture. This was a **pure refactoring** with **zero functionality changes** - the application behaves exactly the same way.

## Architecture

### Before Refactoring
```
NmapDojo/
└── main.py (1159 lines - everything in one file)
```

### After Refactoring
```
NmapDojo/
├── main.py (27 lines - entry point)
│
├── config/
│   ├── __init__.py
│   ├── constants.py        # UI colors, AI config, XP values, topics
│   └── settings.py         # API key, file paths
│
├── models/
│   ├── __init__.py
│   └── types.py            # TypedDict: MissionData, ValidationResult, ProgressData
│
├── core/
│   ├── __init__.py
│   ├── progress_manager.py # Load/save progress, calculate levels
│   ├── mission_generator.py # Generate missions using AI
│   ├── command_validator.py # Validate commands using AI
│   └── ai_service.py       # Google Gemini API integration
│
├── ui/
│   ├── __init__.py
│   ├── app.py              # Main NmapDojoApp class
│   └── components/
│       ├── __init__.py
│       ├── terminal.py     # Terminal panel UI
│       ├── mission_panel.py # Mission control panel UI
│       └── theme.py        # UI styling utilities
│
└── utils/
    ├── __init__.py
    └── logger.py           # Logging configuration
```

## Module Descriptions

### config/
Configuration and constants used throughout the application.

- **constants.py** (63 lines)
  - UI theme colors (hacker dark mode)
  - Font configuration
  - AI model selection
  - XP reward values
  - Level thresholds
  - Topic categories (fundamental & advanced)
  - Application limits (max hints, command history)

- **settings.py** (10 lines)
  - API key configuration
  - File paths (progress file, log file)

### models/
Data type definitions for type safety.

- **types.py** (29 lines)
  - `MissionData`: Mission scenario structure
  - `ValidationResult`: Command validation results
  - `ProgressData`: User progress information

### core/
Business logic and core functionality.

- **progress_manager.py** (76 lines)
  - Load/save user progress from JSON
  - Calculate level based on XP
  - Manage progression state

- **mission_generator.py** (120 lines)
  - Generate missions using AI
  - Topic rotation logic
  - Difficulty scaling based on level
  - Retry logic for API failures

- **command_validator.py** (146 lines)
  - Validate commands against mission requirements
  - Process validation results
  - Award XP and update state
  - Retry logic for API failures

- **ai_service.py** (140 lines)
  - Initialize Google Gemini API
  - Get hints for missions
  - Generate full answers
  - Explain incorrect commands
  - Centralized AI interaction

### ui/
User interface components and application logic.

- **app.py** (757 lines)
  - Main `NmapDojoApp` class
  - UI initialization and setup
  - Event handlers
  - State management
  - Integration of all modules

- **components/terminal.py** (60 lines)
  - Create terminal panel (left side)
  - Terminal output area
  - Command input field
  - Loading indicator

- **components/mission_panel.py** (112 lines)
  - Create mission panel (right side)
  - Stats display (XP, Level)
  - Mission card
  - Action buttons
  - API key input

- **components/theme.py** (34 lines)
  - UI styling utilities
  - Difficulty badge colors
  - Theme-related functions

### utils/
Utility functions and helpers.

- **logger.py** (22 lines)
  - Logging configuration
  - File and console handlers
  - Centralized logger instance

## Key Principles

### 1. No Functionality Changes
Every line of code was copied verbatim from the original `main.py`. The refactoring only reorganized the code, it didn't change any logic, algorithms, or behavior.

### 2. Backward Compatibility
- Existing `dojo_progress.json` files load correctly
- `python main.py` still launches the application
- All dependencies remain the same
- No breaking changes to the API

### 3. Separation of Concerns
Each module has a single, clear responsibility:
- **config**: What values to use
- **models**: What data looks like
- **core**: How things work
- **ui**: How things look
- **utils**: Shared helpers

### 4. Maintainability
- Easier to locate specific functionality
- Changes are isolated to relevant modules
- Reduced risk of unintended side effects
- Simpler to understand and modify

### 5. Testability
- Components can be tested independently
- Mock dependencies easily
- Unit tests for core logic separate from UI

## Benefits

### Development
- **97.7% reduction** in main.py size (1159 → 27 lines)
- Clear module boundaries
- Easier code navigation
- Better IDE support (autocomplete, refactoring)

### Maintenance
- Locate bugs faster
- Understand code flow more easily
- Modify features with confidence
- Add new features without affecting existing code

### Testing
- Test individual components
- Mock external dependencies
- Faster test execution
- Better test coverage

### Collaboration
- Multiple developers can work on different modules
- Clearer code review process
- Reduced merge conflicts
- Better documentation structure

## Migration Guide

### For Users
No changes needed! The application works exactly the same way:
```bash
python main.py
```

### For Developers
Import changes:
```python
# Old (when everything was in main.py)
from main import NmapDojoApp, MissionData, COLOR_SUCCESS

# New (organized imports)
from ui.app import NmapDojoApp
from models import MissionData
from config import COLOR_SUCCESS
```

### Adding New Features
1. Identify the appropriate module (config, core, ui, utils)
2. Add your code to that module
3. Update imports as needed
4. Test your changes

Example: Adding a new topic
```python
# Edit: config/constants.py
FUNDAMENTAL_TOPICS.append("New Topic Name")
```

Example: Adding a new AI feature
```python
# Edit: core/ai_service.py
def get_strategic_advice(self, mission: MissionData) -> str:
    """Get strategic advice for completing a mission."""
    # Implementation here
    pass
```

## Testing

All changes have been verified:
- ✅ All imports work correctly
- ✅ No syntax errors
- ✅ Core components tested
- ✅ Progress file compatibility verified
- ✅ Application starts without errors
- ✅ No functionality changes

## Statistics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| main.py lines | 1159 | 27 | -97.7% |
| Total files | 1 | 19 | +1800% |
| Packages | 0 | 5 | - |
| Largest file | 1159 lines | 757 lines | -34.7% |

## Future Enhancements

The new architecture makes these improvements easier:

1. **Add automated tests**: Test core modules independently
2. **Environment variables**: Move API key to `.env` file
3. **Plugin system**: Add new mission types dynamically
4. **Configuration UI**: Allow users to customize settings
5. **Multiple themes**: Easy to add new UI themes
6. **API abstraction**: Support multiple AI providers
7. **Database support**: Replace JSON with SQLite/PostgreSQL
8. **REST API**: Expose functionality via API endpoints

## Compatibility Notes

- **Python Version**: No change (Python 3.x)
- **Dependencies**: No change (flet, google-generativeai)
- **Data Files**: Compatible with existing progress files
- **API Key**: Still in settings.py (intentional for this refactoring)

## Questions?

The refactoring maintains 100% functionality while improving code organization. If you encounter any issues, they are bugs that need to be fixed, not intended changes.
