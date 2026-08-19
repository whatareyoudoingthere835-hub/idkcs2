#!/usr/bin/env python3
"""
NEVERWIN 2D SANDBOX  (build 7.0.sadge)
=====================================
Оффлайн-песочница: ты стреляешь по ботам, а меню честно портит тебе игру.
НЕ читает память, НЕ лезет в процессы, НЕ требует CS2. Всё — внутри этой
программы на tkinter-canvas.

Управление:
  WASD   — движение
  ЛКМ    — выстрел в сторону курсора
  ПРОБЕЛ — прыжок (заблокирован, если включён ANTI-BHOP)
  INSERT — показать/скрыть оверлей-меню
"""

import math
import random
import tkinter as tk

W, H = 960, 640
ACCENT, ACCENT2, BG = "#22ff88", "#ff2a3c", "#0b0e14"

FONT = ("Consolas", 10)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class Enemy:
    def __init__(self):
        self.x = random.uniform(40, W - 40)
        self.y = random.uniform(40, H - 40)
        self.vx = random.choice([-1, 1]) * random.uniform(0.8, 1.6)
        self.vy = random.choice([-1, 1]) * random.uniform(0.8, 1.6)
        self.r = 14
        self.hp = 2

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.x < self.r or self.x > W - self.r:
            self.vx = -self.vx
        if self.y < self.r or self.y > H - self.r:
            self.vy = -self.vy


class Sandbox:
    def __init__(self, root):
        self.root = root
        self.root.title("NEVERWIN SANDBOX [INSERT = menu]")
        self.root.configure(bg=BG)
        self.root.geometry(f"{W}x{H}")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=W, height=H, bg=BG, bd=0,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # --- игрок и мир ---
        self.px, self.py = W / 2, H / 2
        self.aimx, self.aimy = self.px + 100, self.py
        self.vx = self.vy = 0.0
        self.jumping = False
        self.bullets = []
        self.enemies = [Enemy() for _ in range(6)]
        self.kills = 0
        self.keys = set()

        # --- оружие ---
        self.ammo = 30
        self.mag = 30
        self.reloading = False
        self.reload_t = 0.0
        self.drop_t = 0.0            # оружие выпало (gamesense) — стрелять нельзя

        # --- оверлей-меню ---
        self.show_menu = True
        self.toggles = {
            "anti_aimbot":  tk.BooleanVar(value=False),
            "anti_aimless": tk.BooleanVar(value=False),
            "gamesense":    tk.BooleanVar(value=False),
            "esp":          tk.BooleanVar(value=False),
            "recoil":       tk.BooleanVar(value=False),
            "anti_bhop":    tk.BooleanVar(value=False),
        }
        self.menu_items = []
        self._build_menu()

        self._bind()
        self._loop()

    # ------------------------------------------------------------------ input
    def _bind(self):
        self.root.bind("<KeyPress>", self._key_down)
        self.root.bind("<KeyRelease>", self._key_up)
        self.canvas.bind("<Motion>", self._motion)
        self.canvas.bind("<Button-1>", self._shoot)
        self.root.bind("<Insert>", lambda e: self._toggle_menu())
        self.canvas.focus_set()

    def _key_down(self, e):
        if e.keysym == "Insert":
            self._toggle_menu()
        else:
            self.keys.add(e.keysym)

    def _key_up(self, e):
        self.keys.discard(e.keysym)

    def _motion(self, e):
        self.aimx, self.aimy = e.x, e.y

    # ------------------------------------------------------------------ menu
    def _build_menu(self):
        pad = 12
        w = 300
        f = tk.Frame(self.root, bg="#0e1220", bd=0,
                     highlightbackground="#22ff88", highlightthickness=1)
        f.place(x=pad, y=pad, width=w)
        self.menu_frame = f

        tk.Label(f, text="NEVERWIN  [INSERT]", font=("Consolas", 13, "bold"),
                 fg=ACCENT, bg="#0e1220").pack(anchor="w", padx=10, pady=(8, 2))
        tk.Label(f, text="включи — и пожалеешь", font=FONT,
                 fg="#5b6675", bg="#0e1220").pack(anchor="w", padx=10)
        tk.Frame(f, bg="#1c2333", height=1).pack(fill="x", padx=8, pady=6)

        entries = [
            ("ANTI-AIMBOT",  "прицел бежит ОТ врагов",  "anti_aimbot"),
            ("ANTI-AIMLESS", "встретил врага -> рывок камеры", "anti_aimless"),
            ("GAMESENSE",    "дроп оружия на перезарядке (20%)", "gamesense"),
            ("ESP",          "фейк-коробки врагов",     "esp"),
            ("VISUAL RECOIL", "отдача +400%",             "recoil"),
            ("ANTI-BHOP",    "прыжок заблокирован",      "anti_bhop"),
        ]
        for label, desc, key in entries:
            row = tk.Frame(f, bg="#0e1220")
            row.pack(fill="x", padx=8, pady=3)
            cb = tk.Checkbutton(row, variable=self.toggles[key],
                                text=label, font=("Consolas", 10, "bold"),
                                fg=ACCENT2 if key == "gamesense" else "#c9d4e0",
                                bg="#0e1220", selectcolor="#0e1220",
                                activebackground="#0e1220",
                                activeforeground="#c9d4e0",
                                bd=0)
            cb.pack(side="left", anchor="w")
            tk.Label(row, text=desc, font=("Consolas", 8),
                     fg="#5b6675", bg="#0e1220").pack(anchor="w", padx=24)
            self.menu_items.append(row)

        self.status_lbl = tk.Label(f, text="", font=FONT,
                                   fg="#22ff88", bg="#0e1220",
                                   justify="left")
        self.status_lbl.pack(anchor="w", padx=10, pady=(4, 8))

    def _toggle_menu(self):
        self.show_menu = not self.show_menu
        if self.show_menu:
            self.menu_frame.place(x=12, y=12, width=300)
        else:
            self.menu_frame.place_forget()

    # ------------------------------------------------------------------ helpers
    def nearest_enemy(self):
        best, bd = None, 1e9
        for e in self.enemies:
            d = math.hypot(e.x - self.aimx, e.y - self.aimy)
            if d < bd:
                best, bd = e, d
        return best, bd

    def can_shoot(self):
        return not self.reloading and self.drop_t <= 0 and self.ammo > 0

    # ------------------------------------------------------------------ loop
    def _loop(self):
        self._update(1 / 30)
        self._draw()
        self.root.after(33, self._loop)

    def _update(self, dt):
        s = 4.5
        dx = (self.keys.__contains__("d") or self.keys.__contains__("Right")) - \
             (self.keys.__contains__("a") or self.keys.__contains__("Left"))
        dy = (self.keys.__contains__("s") or self.keys.__contains__("Down")) - \
             (self.keys.__contains__("w") or self.keys.__contains__("Up"))
        if self.toggles["anti_bhop"].get():
            dy = min(dy, 0)  # нельзя идти вперёд/вверх? шутка про "не прыгай"
        self.px = clamp(self.px + dx * s, 20, W - 20)
        self.py = clamp(self.py + dy * s, 20, H - 20)

        # стрельба
        if self.mag == 0 and not self.reloading and self.drop_t <= 0:
            self.reloading = True
            self.reload_t = 1.6
        if self.reloading:
            self.reload_t -= dt
            if self.reload_t <= 0:
                self.reloading = False
                self.mag = self.ammo = 30
                # gamesense: дроп оружия 20%
                if not self.toggles["gamesense"].get() and random.random() < 0.20:
                    self.drop_t = 2.0
                    self.reload_t = 0

        if self.drop_t > 0:
            self.drop_t -= dt

        # --- anti-aimbot: уводим прицел ОТ ближайшего врага ---
        if self.toggles["anti_aimbot"].get():
            e, _ = self.nearest_enemy()
            if e:
                # вектор от врага к прицелу, смещаем в противоположную сторону
                away = math.atan2(self.aimy - e.y, self.aimx - e.x)
                self.aimx += math.cos(away) * 60
                self.aimy += math.sin(away) * 60
        if self.toggles["anti_aimless"].get():
            e, d = self.nearest_enemy()
            if e and d < 260:
                # рывок камеры в случайную дальнюю точку
                self.aimx = random.uniform(0, W)
                self.aimy = random.uniform(0, H)

        # пули
        for b in self.bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            hit = False
            for e in self.enemies[:]:
                if math.hypot(b[0] - e.x, b[1] - e.y) < e.r + 4:
                    e.hp -= 1
                    if e.hp <= 0:
                        self.enemies.remove(e)
                        self.kills += 1
                    hit = True
                    break
            if hit or not (0 <= b[0] <= W and 0 <= b[1] <= H):
                self.bullets.remove(b)

        # враги
        for e in self.enemies:
            e.update()
        # респавн
        if not self.enemies and len(self.enemies) == 0:
            if random.random() < 0.02:
                self.enemies.append(Enemy())

        # hud-статус
        status = f"kills: {self.kills}   mag: {self.mag}"
        if self.reloading:
            status += "  [RELOAD...]"
        if self.drop_t > 0:
            status += "  [ORUZHIE UPALO!]"
        self.status_lbl.config(text=status)

    def _shoot(self, _e):
        if not self.can_shoot():
            return
        self.mag -= 1
        ang = math.atan2(self.aimy - self.py, self.aimx - self.px)
        spread = 0.0
        if self.toggles["recoil"].get():
            spread = random.uniform(-0.55, 0.55)   # +400% отдачи: дикий разлёт
        ang += spread
        sp = 14
        self.bullets.append([self.px, self.py,
                             math.cos(ang) * sp, math.sin(ang) * sp])

    # ------------------------------------------------------------------ draw
    def _draw(self):
        c = self.canvas
        c.delete("all")
        c.create_rectangle(0, 0, W, H, fill="#0b0e14", outline="")

        # решётка
        for x in range(0, W, 40):
            c.create_line(x, 0, x, H, fill="#121826")
        for y in range(0, H, 40):
            c.create_line(0, y, W, y, fill="#121826")

        # ESP: фейк-коробки там, где врагов нет
        if self.toggles["esp"].get():
            for i in range(5):
                fx = (self.px + 160 * math.cos(i * 2.5) + 50 * (i % 3)) % W
                fy = (self.py + 160 * math.sin(i * 2.5) + 40) % H
                c.create_rectangle(fx - 18, fy - 18, fx + 18, fy + 18,
                                   outline="#ff22aa", width=2)
                c.create_line(fx - 18, fy - 26, fx + 18, fy - 26,
                              fill="#ff22aa", width=1)

        # враги
        for e in self.enemies:
            c.create_rectangle(e.x - e.r, e.y - e.r, e.x + e.r, e.y + e.r,
                               fill="#3a0f16", outline="#ff2a3c", width=2)
            c.create_line(e.x, e.y - e.r, e.x, e.y + e.r, fill="#ff2a3c")

        # пули
        for b in self.bullets:
            c.create_oval(b[0] - 3, b[1] - 3, b[0] + 3, b[1] + 3,
                          fill="#22ff88", outline="")

        # игрок
        c.create_oval(self.px - 12, self.py - 12, self.px + 12, self.py + 12,
                      fill="#0f2a1a", outline="#22ff88", width=2)

        # прицел
        c.create_line(self.aimx - 10, self.aimy, self.aimx + 10, self.aimy,
                      fill="#22ff88")
        c.create_line(self.aimx, self.aimy - 10, self.aimx, self.aimy + 10,
                      fill="#22ff88")

        if self.drop_t > 0:
            c.create_text(W / 2, 60, text="ORUZHIE VYPALO! podberi...",
                          fill="#ff2a3c", font=("Consolas", 18, "bold"))


def main():
    root = tk.Tk()
    Sandbox(root)
    root.mainloop()


if __name__ == "__main__":
    main()
