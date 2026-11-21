---
name: test-runner
description: Verify and test Python and Pygame scripts using the local virtual environment.
---

Help verify and test the Python files in this project:

1. **Locate Virtual Environment**: Use the project's local virtual environment at `.venv\Scripts\python.exe`.
2. **Bytecode Compilation Check**:
   ```powershell
   & ".\.venv\Scripts\python.exe" -m py_compile "<filename>.py"
   ```
3. **Headless Pygame Initialization Check**:
   ```powershell
   $env:SDL_VIDEODRIVER="dummy"; & ".\.venv\Scripts\python.exe" -c "import pygame; pygame.init(); print('Pygame initialized successfully')"
   ```
4. **Report Results**: Provide a clear summary of any compilation errors, missing dependencies, or runtime issues found.
