# 🏹 Medieval Rogue

A pixel-style roguelite inspired by *The Binding of Isaac*, but with a medieval dark-fantasy theme.  
Fight through randomly generated dungeon rooms, collect items, defeat bosses, and try to get the highest score!

> ⚠️ Windows users: a ready-to-run `launcher.exe` is available in the repository.

---

## 🎮 Features

- **Procedurally generated dungeon floors** (currently 3 floors, more patterns).
- **Playable classes:** Archer, Rogue, Mage.
- **Sprites & visual overhaul**:
  - Hand-made + AI-assisted pixel art sprites for floors, walls, enemies, bosses, doors, and items.
- **Lighting & atmosphere**:
  - Torches with flickering light.
  - Smooth edge-fade from room interior to screen borders.
- **Expanded content**:
  - More room patterns.
  - More items that affect stats and health.
  - 3 enemy types + 4 unique bosses.
- **Scoring system**:
  - \+ points for enemies, rooms, bosses.
  - −1 point per second (time matters!).
- **Performance improvements** for smoother gameplay.

Version **2.0.0** is the new major update 🚀

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
or simply:
```bash
python launcher.py
```

The game runs in base resolution **1280×736**, scaled to your window/screen.

---

## 🕹 Controls
- **WASD** — Move  
- **Mouse** — Aim  
- **Left Click** — Shoot  
- **N** — Advance to next floor after boss defeat  
- **Esc** — Exit to menu  

---

## 📖 Version Log

### [2.0.0] — 2025-10-01
- Major visual update:
  - Sprites for tiles, walls, doors, obstacles, enemies, and bosses.
  - All pixel art made by me with help of AI.  
- New lighting system with torches and edge fade.
- More room patterns and obstacles.
- Items updated.
- Boss flow improved: prompt to press **N** after boss defeat.
- General performance improvements.

### [1.0.1] — 2025-08-24
- Features:
  - Add sfx sounds for shooting and being hit.
  - Add `.exe` build for Windows and launcher.py shortcut.

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

---

#### 🎨 Sprite Credits
All sprites were made by me, with help of AI (ChatGPT image generation).

#### 🔊 Sound Credits
- arrow_shot.wav by Lydmakeren — [freesound.org/s/511490](https://freesound.org/s/511490/) — License: CC0  
- player_hit.wav by MrFossy — [freesound.org/s/547204](https://freesound.org/s/547204/) — License: CC0
