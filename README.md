# Neon Snake: Remastered Edition

A sleek, modern 2D retro-arcade Snake game built with Pygame, featuring a 60 FPS deterministic engine, pre-baked neon glow aesthetics, particle simulation, and power-up mechanics.

---

## Features
- **Smooth 60 FPS Game Engine**: Fluid neon particle bursts, pulsing glow halos, and screen shake running with discrete grid movement.
- **Power-Up Fruits**:
  - 🍎 **Apple**: Regular fruit (`+10 pts`, increases length).
  - ⭐ **Golden Apple**: Rare bonus fruit (`+30 pts`, spawns every 5 regular foods for 10 seconds).
  - ❄️ **Freeze Berry**: Slow-motion mode (halves snake speed for 6 seconds to help navigate tricky spaces).
  - 🔮 **Ghost Berry**: Phase-shift mode (turns the snake translucent and lets you pass through your own tail for 6 seconds).
- **Audio System**: Built-in zero-dependency MIDI synthesizer with melodic jingles and an instant mute toggle.
- **State Machine Architecture**: Clean separation between Menu, Gameplay, Pause, and Game Over states.

---

## Controls
- **Arrow Keys / WASD**: Steer the snake (buffered input prevents self-collision turns).
- **P / Esc**: Pause / Resume the game.
- **M**: Toggle audio mute on/off.
- **Enter / Space**: Start game / Play again.

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
