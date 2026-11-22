# Neon Snake: Remastered Edition

A sleek, modern 2D retro-arcade Snake game built with Pygame, featuring a 60 FPS deterministic engine, pre-baked neon glow aesthetics, progressive dynamic arenas, quantum teleporters, and a tactical AI rival / local 2-player duel engine.

---

## 4 Game Modes

1. **Classic Endless**:
   - Progressive dynamic arenas: As your score rises, central barrier walls materialize (Tier 2: 40 pts) and Paired Quantum Portals activate (Tier 3: 80 pts).
   - High-score chasing with rare power-up fruits.
2. **Time Attack**:
   - 45-second starting countdown clock.
   - Regular food adds `+3 seconds`; special fruits add `+5 seconds`.
   - Test your speed and efficiency before the clock expires!
3. **Maze Survival**:
   - Navigate a dense geometric neon labyrinth with tight corridors and deadly barrier walls.
4. **Versus Duel (1v1)**:
   - **Play vs Aggressive AI Rival** or **Local Player 2** on the same keyboard.
   - Best-of-3 rounds: Trap your opponent, force collisions, or race to 100 points!

---

## Power-Up Fruits & Quantum Mechanics

- 🍎 **Apple**: Regular fruit (`+10 pts`, growth +1).
- ⭐ **Golden Apple**: Rare bonus fruit (`+30 pts`, spawns every 5 fruits for 10s).
- ❄️ **Freeze Berry**: Slow-motion mode (halves snake speed for 6 seconds).
- 🔮 **Ghost Berry**: Phase-shift mode (turns translucent and passes through your own tail for 6 seconds).
- 🌀 **Quantum Portals**: Paired color-coded gates (Blue $\leftrightarrow$ Violet). Enter one gate to instantly warp across the board with preserved momentum.

---

## Controls

### Single-Player (Classic, Time Attack, Maze Survival)
- **Arrow Keys / WASD**: Steer the snake.
- **P / Esc**: Pause / Resume.
- **M**: Toggle audio mute on/off.
- **Enter / Space**: Start game / Play again.

### Versus Duel (Local 2-Player or vs AI)
- **Player 1 (Cyan Snake)**: `W`, `A`, `S`, `D`
- **Player 2 (Amber Snake)**: `Up`, `Down`, `Left`, `Right` *(or controlled by Aggressive AI)*

---

## How to Run

1. Activate your virtual environment and install dependencies:
```powershell
python -m pip install -r requirements.txt
```

2. Run the game:
```powershell
python snake_game.py
```
