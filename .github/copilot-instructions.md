# Developer & Game Development Guidelines for Copilot / VS Code

## 1. General Principles
- Write clean, readable, and maintainable code with clear modular boundaries.
- Prefer explicit logic over complex abstractions.
- Follow defensive programming: validate inputs, handle edge cases gracefully, and provide descriptive error messages.

## 2. Python Standards
- **Style**: Follow PEP 8 guidelines. Use 4 spaces for indentation and meaningful snake_case names for variables and functions, PascalCase for classes, and UPPER_CASE for constants.
- **Type Hints**: Include type hints on function signatures and return values to improve readability and tooling support.
- **Virtual Environments**: Always use the project's dedicated virtual environment (`.venv` or `venv`) for running scripts and installing packages (e.g., `.\.venv\Scripts\python.exe`).
- **Imports**: Group imports into standard library, third-party packages, and local modules.

## 3. Pygame & 2D Game Development
- **Game Loop Structure**: Maintain a clear, deterministic loop:
  1. *Event Handling*: Process `pygame.event.get()` (keyboard, mouse, window events).
  2. *Game State Update*: Update positions, check collisions, and evaluate game rules.
  3. *Render*: Clear/fill screen background, blit game entities, and flip or update display.
  4. *Clock Tick*: Cap framerate with `clock.tick(FPS)` to ensure consistent speed across hardware.
- **Resource Management**:
  - Never load fonts, sound effects, or images inside the main game loop (`while running`). Pre-load all assets during initialization.
  - Use relative path resolution (e.g., `pathlib.Path(__file__).parent / "assets"`) so games run consistently regardless of the working directory.
- **State Separation**:
  - Keep state logic separate from drawing routines.
  - Implement a simple state machine or state flags (e.g., `MENU`, `PLAYING`, `PAUSED`, `GAME_OVER`) rather than mixing all states in a single block.
- **Clean Shutdown**:
  - Always call `pygame.quit()` followed by `sys.exit()` on exit events to prevent hanging processes or window freezing.

## 4. Assistant Behavior & Communication
- Explain the root cause when diagnosing bugs before proposing fixes.
- Provide clean, functional code edits rather than partial snippets.
- Use clickable `file:///` links when referencing files or scripts.
