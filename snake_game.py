"""A polished Snake game using only Python's standard library.

Run:
    python snake_game.py

Controls:
    Arrow keys / WASD   Move
    Space / P           Pause or resume
    R                   Restart
    Esc                 Quit
"""

from __future__ import annotations

import random
import tkinter as tk
from collections import deque

# ---------------------------------------------------------------------------
# Layout and theme
# ---------------------------------------------------------------------------

COLS = 24
ROWS = 24
CELL = 24
BOARD_SIZE = COLS * CELL

BOARD_X = 24
BOARD_Y = 76
WIDTH = BOARD_X * 2 + BOARD_SIZE
HEIGHT = BOARD_Y + BOARD_SIZE + 20

BASE_DELAY = 115          # milliseconds between moves
MIN_DELAY = 55
SPEED_STEP = 3.5          # milliseconds shaved off per apple
POINTS_PER_APPLE = 10

COLORS = {
    "bg": "#07100d",
    "board": "#0b1814",
    "board_line": "#122a23",
    "border": "#234a3d",
    "green": "#57e39a",
    "green_bright": "#8dffc1",
    "green_dark": "#1f7657",
    "text": "#e9fff5",
    "muted": "#759487",
    "red": "#ff5f70",
    "red_light": "#ffb3ba",
    "gold": "#ffd166",
    "card": "#10251e",
    "card_border": "#2e6250",
}

FONT = "Segoe UI"
MONO = "Consolas"

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
    "w": (0, -1),
    "s": (0, 1),
    "a": (-1, 0),
    "d": (1, 0),
}


class SnakeGame:
    """Main game window and loop."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Snake")
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(
            root,
            width=WIDTH,
            height=HEIGHT,
            bg=COLORS["bg"],
            highlightthickness=0,
        )
        self.canvas.pack()

        self._center_window()

        self.best = 0
        self.after_id: str | None = None
        self.state = "ready"

        self.root.bind("<KeyPress>", self._on_key)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

        self._reset()

    # ------------------------------------------------------------------
    # Game setup
    # ------------------------------------------------------------------

    def _center_window(self) -> None:
        self.root.update_idletasks()
        x = max(0, (self.root.winfo_screenwidth() - WIDTH) // 2)
        y = max(0, (self.root.winfo_screenheight() - HEIGHT) // 2 - 20)
        self.root.geometry(f"{WIDTH}x{HEIGHT}+{x}+{y}")

    def _reset(self) -> None:
        self._cancel_tick()

        start_x = COLS // 2
        start_y = ROWS // 2
        self.snake: list[tuple[int, int]] = [
            (start_x, start_y),
            (start_x - 1, start_y),
            (start_x - 2, start_y),
            (start_x - 3, start_y),
        ]

        self.direction = (1, 0)
        self.direction_queue: deque[tuple[int, int]] = deque()
        self.score = 0
        self.eaten = 0
        self.delay = BASE_DELAY
        self.best_at_start = self.best
        self.won = False
        self.food: tuple[int, int] | None = None
        self._spawn_food()

        self.state = "ready"
        self._draw()

    def _spawn_food(self) -> bool:
        occupied = set(self.snake)
        free = [
            (x, y)
            for y in range(ROWS)
            for x in range(COLS)
            if (x, y) not in occupied
        ]
        if not free:
            self.food = None
            return False
        self.food = random.choice(free)
        return True

    # ------------------------------------------------------------------
    # Game clock
    # ------------------------------------------------------------------

    def _schedule_tick(self) -> None:
        self._cancel_tick()
        self.after_id = self.root.after(self.delay, self._tick)

    def _cancel_tick(self) -> None:
        if self.after_id is not None:
            try:
                self.root.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

    def _begin(self) -> None:
        if self.state != "ready":
            return
        self.state = "running"
        self._draw()
        self._schedule_tick()

    def _pause(self) -> None:
        if self.state != "running":
            return
        self.state = "paused"
        self._cancel_tick()
        self._draw()

    def _resume(self) -> None:
        if self.state != "paused":
            return
        self.state = "running"
        self._draw()
        self._schedule_tick()

    def _end_game(self, won: bool = False) -> None:
        self._cancel_tick()
        self.state = "gameover"
        self.won = won
        self._draw()

    def _tick(self) -> None:
        self.after_id = None
        if self.state != "running":
            return

        if self.direction_queue:
            self.direction = self.direction_queue.popleft()

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self._end_game()
            return

        will_eat = new_head == self.food
        # The tail moves away this turn unless the snake is growing.
        body = self.snake if will_eat else self.snake[:-1]
        if new_head in body:
            self._end_game()
            return

        self.snake.insert(0, new_head)

        if will_eat:
            self.score += POINTS_PER_APPLE
            self.eaten += 1
            if self.score > self.best:
                self.best = self.score
            self.delay = max(MIN_DELAY, int(BASE_DELAY - self.eaten * SPEED_STEP))

            if not self._spawn_food():
                self._draw()
                self._end_game(won=True)
                return
        else:
            self.snake.pop()

        self._draw()
        self._schedule_tick()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _queue_direction(self, dx: int, dy: int) -> None:
        last = self.direction_queue[-1] if self.direction_queue else self.direction
        if (dx, dy) == last or (dx, dy) == (-last[0], -last[1]):
            return
        if len(self.direction_queue) < 2:
            self.direction_queue.append((dx, dy))

    def _on_key(self, event: tk.Event) -> str:
        key = event.keysym.lower()

        if key == "escape":
            self._close()
            return "break"

        if self.state == "gameover":
            if key in ("space", "return"):
                self._reset()
                self._begin()
            elif key == "r":
                self._reset()
            return "break"

        if self.state == "paused":
            if key in ("space", "p"):
                self._resume()
            elif key == "r":
                self._reset()
            return "break"

        if self.state == "ready":
            if key in DIRECTIONS:
                self.direction = DIRECTIONS[key]
                self.direction_queue.clear()
                self._begin()
            elif key in ("space", "return"):
                self._begin()
            return "break"

        # Running
        if key in DIRECTIONS:
            self._queue_direction(*DIRECTIONS[key])
        elif key in ("space", "p"):
            self._pause()
        elif key == "r":
            self._reset()

        return "break"

    def _close(self) -> None:
        self._cancel_tick()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Drawing helpers
    # ------------------------------------------------------------------

    def _rounded_rect(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        radius: float,
        **kwargs: object,
    ) -> int:
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.canvas.create_polygon(
            points,
            smooth=True,
            splinesteps=12,
            **kwargs,
        )

    @staticmethod
    def _blend(color_a: str, color_b: str, amount: float) -> str:
        a = tuple(int(color_a[i : i + 2], 16) for i in (1, 3, 5))
        b = tuple(int(color_b[i : i + 2], 16) for i in (1, 3, 5))
        mixed = tuple(round(a[i] + (b[i] - a[i]) * amount) for i in range(3))
        return f"#{mixed[0]:02x}{mixed[1]:02x}{mixed[2]:02x}"

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _draw(self) -> None:
        self.canvas.delete("all")
        self._draw_header()
        self._draw_board_background()
        self._draw_food()
        self._draw_snake()
        self._draw_overlay()

    def _draw_header(self) -> None:
        self.canvas.create_text(
            BOARD_X,
            13,
            text="SCORE",
            anchor="nw",
            fill=COLORS["muted"],
            font=(FONT, 8, "bold"),
        )
        self.canvas.create_text(
            BOARD_X,
            29,
            text=f"{self.score:03d}",
            anchor="nw",
            fill=COLORS["text"],
            font=(MONO, 24, "bold"),
        )

        self.canvas.create_text(
            WIDTH - BOARD_X,
            13,
            text="BEST",
            anchor="ne",
            fill=COLORS["muted"],
            font=(FONT, 8, "bold"),
        )
        self.canvas.create_text(
            WIDTH - BOARD_X,
            29,
            text=f"{self.best:03d}",
            anchor="ne",
            fill=COLORS["gold"],
            font=(MONO, 24, "bold"),
        )

        self.canvas.create_text(
            WIDTH // 2,
            25,
            text="SNAKE",
            anchor="center",
            fill=COLORS["green"],
            font=(FONT, 23, "bold"),
        )

        labels = {
            "ready": ("READY", COLORS["muted"]),
            "running": ("PLAYING", COLORS["green"]),
            "paused": ("PAUSED", COLORS["gold"]),
            "gameover": ("YOU WIN" if self.won else "GAME OVER", COLORS["red"]),
        }
        label, color = labels[self.state]
        self.canvas.create_text(
            WIDTH // 2,
            53,
            text=label,
            anchor="center",
            fill=color,
            font=(FONT, 8, "bold"),
        )

        self.canvas.create_line(
            BOARD_X,
            BOARD_Y - 3,
            WIDTH - BOARD_X,
            BOARD_Y - 3,
            fill="#102a22",
            width=1,
        )

    def _draw_board_background(self) -> None:
        self.canvas.create_rectangle(
            BOARD_X,
            BOARD_Y,
            BOARD_X + BOARD_SIZE,
            BOARD_Y + BOARD_SIZE,
            fill=COLORS["board"],
            outline=COLORS["border"],
            width=1,
        )

        for col in range(1, COLS):
            x = BOARD_X + col * CELL
            self.canvas.create_line(
                x,
                BOARD_Y,
                x,
                BOARD_Y + BOARD_SIZE,
                fill=COLORS["board_line"],
                width=1,
            )

        for row in range(1, ROWS):
            y = BOARD_Y + row * CELL
            self.canvas.create_line(
                BOARD_X,
                y,
                BOARD_X + BOARD_SIZE,
                y,
                fill=COLORS["board_line"],
                width=1,
            )

    def _cell_center(self, cell: tuple[int, int]) -> tuple[float, float]:
        x, y = cell
        return (
            BOARD_X + x * CELL + CELL / 2,
            BOARD_Y + y * CELL + CELL / 2,
        )

    def _draw_food(self) -> None:
        if self.food is None:
            return

        cx, cy = self._cell_center(self.food)

        # Soft glow
        self.canvas.create_oval(
            cx - 11, cy - 11, cx + 11, cy + 11,
            fill="#3c191d",
            outline="",
        )
        # Apple body
        self.canvas.create_oval(
            cx - 7, cy - 6, cx + 7, cy + 8,
            fill=COLORS["red"],
            outline="#ff8f99",
            width=1,
        )
        # Shine
        self.canvas.create_oval(
            cx - 4, cy - 3, cx - 1, cy + 1,
            fill="#ffd9dd",
            outline="",
        )
        # Stem
        self.canvas.create_line(
            cx, cy - 8, cx + 2, cy - 12,
            fill="#8a5a3b",
            width=2,
            capstyle="round",
        )
        # Leaf
        self.canvas.create_oval(
            cx + 2, cy - 12, cx + 9, cy - 8,
            fill=COLORS["green"],
            outline="",
        )

    def _draw_snake(self) -> None:
        length = len(self.snake)

        # Body, from tail to neck.
        for index in range(length - 1, 0, -1):
            x, y = self.snake[index]
            amount = index / max(length - 1, 1)
            color = self._blend(COLORS["green"], COLORS["green_dark"], amount)
            pad = 3
            self._rounded_rect(
                BOARD_X + x * CELL + pad,
                BOARD_Y + y * CELL + pad,
                BOARD_X + (x + 1) * CELL - pad,
                BOARD_Y + (y + 1) * CELL - pad,
                6,
                fill=color,
                outline="",
            )

        # Head.
        hx, hy = self.snake[0]
        pad = 1.5
        self._rounded_rect(
            BOARD_X + hx * CELL + pad,
            BOARD_Y + hy * CELL + pad,
            BOARD_X + (hx + 1) * CELL - pad,
            BOARD_Y + (hy + 1) * CELL - pad,
            8,
            fill=COLORS["green_bright"],
            outline="#b9ffdc",
            width=1,
        )

        # Eyes point in the direction of travel.
        cx, cy = self._cell_center((hx, hy))
        dx, dy = self.direction
        px, py = -dy, dx

        for side in (-1, 1):
            ex = cx + dx * 4 + px * 4.5 * side
            ey = cy + dy * 4 + py * 4.5 * side
            self.canvas.create_oval(
                ex - 3, ey - 3, ex + 3, ey + 3,
                fill="#f4fff9",
                outline="",
            )
            self.canvas.create_oval(
                ex + dx * 1.2 - 1.5,
                ey + dy * 1.2 - 1.5,
                ex + dx * 1.2 + 1.5,
                ey + dy * 1.2 + 1.5,
                fill="#06110d",
                outline="",
            )

    def _draw_overlay(self) -> None:
        if self.state == "running":
            return

        # Dim the play field.
        self.canvas.create_rectangle(
            BOARD_X + 1,
            BOARD_Y + 1,
            BOARD_X + BOARD_SIZE - 1,
            BOARD_Y + BOARD_SIZE - 1,
            fill="#020b08",
            outline="",
            stipple="gray50",
        )

        center_x = WIDTH // 2
        center_y = BOARD_Y + BOARD_SIZE // 2
        card_w = 430
        card_h = 216
        x1 = center_x - card_w // 2
        y1 = center_y - card_h // 2
        x2 = center_x + card_w // 2
        y2 = center_y + card_h // 2

        self._rounded_rect(
            x1, y1, x2, y2, 18,
            fill=COLORS["card"],
            outline=COLORS["card_border"],
            width=1,
        )

        if self.state == "ready":
            self._overlay_text(center_x, center_y - 63, "SNAKE", 30, COLORS["green"])
            self._overlay_text(
                center_x,
                center_y - 24,
                "Eat apples. Avoid the walls and yourself.",
                10,
                COLORS["muted"],
            )
            self._overlay_text(
                center_x,
                center_y + 22,
                "Press an arrow key or WASD to start",
                12,
                COLORS["text"],
            )
            self._overlay_text(
                center_x,
                center_y + 58,
                "Space: pause    R: restart    Esc: quit",
                9,
                COLORS["muted"],
            )

        elif self.state == "paused":
            self._overlay_text(center_x, center_y - 47, "PAUSED", 30, COLORS["gold"])
            self._overlay_text(
                center_x,
                center_y + 4,
                "Press Space or P to resume",
                12,
                COLORS["text"],
            )
            self._overlay_text(
                center_x,
                center_y + 47,
                "R: restart    Esc: quit",
                9,
                COLORS["muted"],
            )

        else:  # game over / win
            if self.won:
                self._overlay_text(
                    center_x, center_y - 65, "YOU WIN!", 30, COLORS["gold"]
                )
            else:
                self._overlay_text(
                    center_x, center_y - 65, "GAME OVER", 28, COLORS["red"]
                )

            self._overlay_text(
                center_x,
                center_y - 23,
                f"SCORE   {self.score}",
                15,
                COLORS["text"],
            )

            best_color = COLORS["gold"] if self.score > self.best_at_start else COLORS["muted"]
            best_text = f"BEST   {self.best}"
            if self.score > self.best_at_start:
                best_text += "   NEW BEST!"
            self._overlay_text(
                center_x,
                center_y + 8,
                best_text,
                10,
                best_color,
            )

            self._overlay_text(
                center_x,
                center_y + 49,
                "Press Space to play again",
                12,
                COLORS["green"],
            )
            self._overlay_text(
                center_x,
                center_y + 76,
                "R: reset    Esc: quit",
                9,
                COLORS["muted"],
            )

    def _overlay_text(
        self,
        x: float,
        y: float,
        text: str,
        size: int,
        color: str,
    ) -> None:
        self.canvas.create_text(
            x,
            y,
            text=text,
            anchor="center",
            fill=color,
            font=(FONT, size, "bold" if size >= 12 else "normal"),
        )


def main() -> None:
    root = tk.Tk()
    SnakeGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
