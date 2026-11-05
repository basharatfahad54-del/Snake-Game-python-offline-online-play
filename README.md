# Snake Game — Python

A polished Snake game with two ways to play:

- **Browser edition** — play instantly, no installation required.
- **Desktop edition** — built entirely with Python's standard library and Tkinter.

<p align="center">
  <a href="https://fahad000786.github.io/snake-game-python/">
    <img src="assets/snake-web-play.png" alt="Snake browser game" width="460">
  </a>
</p>

<p align="center">
  <a href="https://fahad000786.github.io/snake-game-python/"><strong>▶ Play Snake in your browser</strong></a>
</p>

## Play online

**https://fahad000786.github.io/snake-game-python/**

The browser edition lives in [`docs/index.html`](docs/index.html) and is published with GitHub Pages. It supports keyboard, swipe, and on-screen touch controls, and saves your best score locally in your browser.

## Desktop edition

<p align="center">
  <img src="assets/snake-game.png" alt="Snake desktop game" width="400">
</p>

Run it with:

```bash
python snake_game.py
```

## Controls

| Input | Action |
| --- | --- |
| Arrow keys / `WASD` | Move |
| Swipe or on-screen pad | Move (browser/mobile) |
| `Space` / `P` | Pause or resume |
| `R` | Restart |
| `Esc` | Quit (desktop) |

## Features

- Classic 24 × 24 grid with wall and self collisions
- Score, best score, and an in-game HUD
- Speed increases as you eat apples
- Ready, paused, game-over, and win screens
- Keyboard, swipe, and touch controls in the browser
- Dark theme with a custom-drawn snake, apple, and rounded UI
- No third-party Python packages required

## Project structure

```text
snake_game.py       Python + Tkinter desktop game
docs/index.html     Browser edition (GitHub Pages)
assets/             Screenshots
```

## Requirements

Desktop edition: Python 3 with Tkinter (included with the standard Windows and macOS installers).  
Browser edition: any modern browser.
