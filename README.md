# 🏹 Medieval Rogue

A pixel-style roguelite inspired by *The Binding of Isaac*, but with a medieval theme.  
Fight through randomly generated dungeon rooms, collect items, defeat bosses, and try to get the highest score!

> ⚠️ Windows users: a ready-to-run `MedievalRogue.exe` can be found in the `dist` folder (see the **Windows executable** section below).

---

## 🎮 Features
- Procedurally generated dungeon floors (currently 3 floors).
- One playable class: **Archer** (shoot arrows).
- 3 enemy types + 3 bosses.
- 5 items to boost your stats.
- Scoring system:
  - \+ points for enemies, rooms, bosses.
  - -1 point per second (time matters!).
- Room obstacles and collision system.

Version **1.0.0** is the first fully playable release 🚀

---

## 🛠 Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/vpow10/Python-RPG-Pixel-Game.git
cd medieval-rogue
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows PowerShell
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the game
```bash
python -m medieval_rogue
```
or simply 
```bash
python launcher.py
```

The game runs in base resolution **320×180**, scaled to your window/screen.

---

## 📦 Windows executable (ready-to-run)

A ready-to-run Windows executable is provided in the `dist` folder after building:

- Path (after build): `dist/MedievalRogue/MedievalRogue.exe`
- To run: double-click `MedievalRogue.exe` or open a command prompt in the `dist/MedievalRogue` folder and run:
```cmd
.\MedievalRogue.exe
```
---

## 🕹 Controls
- **WASD** — Move  
- **Mouse** — Aim  
- **Left Click** — Shoot  
- **E** — Pick up item  
- **Space** — Advance to next room after clear  
- **Esc** — Exit to menu  

---

## 📖 Version Log

### [1.0.0] — 2025-08-23
- Initial fully playable version 🎉
- Features:
  - 3 floors with random rooms
  - 3 enemy types, 3 bosses
  - Archer class
  - 5 items
  - Basic scoring & HUD
  - Collisions, hitstop, invulnerability frames

---

### Future updates
- New characters & classes.
- More items, enemies, bosses.
- Expanded dungeon layouts.
- Polished menus, sounds, and effects.

*(This log will always keep the last 5 versions.)*

#### 🔊 Sound Credits
- arrow_shot.wav by Lydmakeren -- https://freesound.org/s/511490/ -- License: Creative Commons 0
- player_hit.wav by MrFossy -- https://freesound.org/s/547204/ -- License: Creative Commons 0