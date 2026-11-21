---
name: code-review
description: Perform a rigorous, constructive code review checking for logic errors, performance issues, security risks, and style standards.
---

Review the currently open or specified Python/Pygame files:

1. **Logic & Edge Cases**: Identify unhandled edge cases (zero division, empty collections, missing boundary checks).
2. **Pygame Architecture**: Verify asset preloading, proper game loop separation (events -> update -> render -> clock.tick), and state handling.
3. **Performance & Memory**: Ensure no font or image reloading occurs in the game loop.
4. **Style & Types**: Check PEP 8 compliance, clear naming conventions, and type annotations.

Format your response with:
- **Verdict / Summary**
- **Critical / High Priority Issues** (with line numbers and concrete fixes)
- **Suggested Improvements & Optimizations**
