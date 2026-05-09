# Desktop Pet — Pixel Art Retro Companion

A pixel-art slime companion that lives on your macOS desktop. Feed it, play with it, watch it grow, and discover its story.

## Features

- **Non-intrusive** — No popups, no notifications. Lives quietly in a corner
- **Pixel art retro style** — 16x16 sprites at 10x scale, Game-Boy-era aesthetic
- **4 growth stages** — Baby > Child > Teen > Adult, evolving over hours of playtime
- **Needs system** — Hunger, happiness, energy decay in real time
- **Story events** — 15 scripted events triggered by stage, playtime, and conditions
- **Right-click menu** — Feed, play, talk, status, always-on-top toggle
- **Persistent save** — JSON save at `~/.desktop_pet/`, offline decay included
- **Ultra low resource** — 12 FPS, ~2100 lines of Python, minimal CPU usage

## Quick Start

```bash
# Requires Python 3.10+ and pygame
pip install pygame
python3 main.py
```

**Controls:**

| Action | How |
|--------|-----|
| Move window | Left-click drag |
| Interact | Right-click menu |
| Feed | `F` or menu |
| Play | `P` or menu |
| Talk | `T` or menu |
| Sleep | `S` or menu |
| Quit | `Q` / `Esc` / menu |

**Test mode:** `python3 main.py --fast` (60x speed for testing growth and events)

## How It Works

```
desktop_pet/
├── main.py              # Game loop, window, input
├── config.py            # Constants, palette, tuning
├── sprites.py           # 16x16 pixel art (ASCII-defined)
├── sprite_renderer.py   # Cache-based scaled rendering
├── animation.py         # Frame timing, loops
├── pet.py               # Core pet orchestrator
├── state_machine.py     # 8 behavior states
├── needs.py             # Hunger/happiness/energy decay
├── event_system.py      # 15 story events, triggers
├── dialog.py            # Typewriter dialog overlay
├── context_menu.py      # Right-click tkinter menu
├── window_manager.py    # SDL2 always-on-top, opacity
├── save_manager.py      # JSON persistence
└── particles.py         # Sparkle/heart effects
```

The pet doesn't die. Needs bottom out at 0 — it just looks sad. Feed it a few times and it bounces back.

## License

MIT
