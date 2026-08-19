#!/usr/bin/env python3
"""
NEVERWIN v6.9.420
=================
Экстернал чит, который гарантирует, что ты НИКОГДА не выиграешь.

Это пародийный / мемный проект: все "фичи" специально ломают тебе игру.
Ничего не читает и не пишет в чужие процессы, античит не трогает,
использовать для читерства нельзя (да и незачем — это саботаж).

Вкладки:
  COMBAT   -> anti-aimbot, anti-aimless, gamesense (дроп оружия)
  RENDER   -> ESP (фейк-позиции), visual recoil (+400%)
  MOVEMENT -> anti-bhop
"""

import datetime
import random
import tkinter as tk

APP_NAME = "NEVERWIN"
BUILD = "build 6.9.420"
BG      = "#0b0e14"
BG_PANEL= "#11151f"
BG_NAV  = "#0e1220"
ACCENT  = "#22ff88"
ACCENT2 = "#ff2a3c"
TXT     = "#c9d4e0"
DIM     = "#5b6675"
LINE    = "#1c2333"

FONT = ("Consolas", 10)
FONT_BIG = ("Consolas", 15, "bold")


class NeverWin:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME}  [{BUILD}]")
        self.root.configure(bg=BG)
        self.root.geometry("880x620")
        self.root.minsize(760, 540)

        # --- состояние переключателей ---
        self.anti_aimbot  = tk.BooleanVar(False)
        self.anti_aimless = tk.BooleanVar(False)
        self.gamesense    = tk.BooleanVar(False)
        self.esp          = tk.BooleanVar(False)
        self.recoil       = tk.BooleanVar(False)
        self.anti_bhop    = tk.BooleanVar(False)
        self.fps_var      = tk.StringVar(value="0 FPS")

        self._build_ui()
        self.log(f"[NEVERWIN] загружен. Удачи. Тебе она понадобится.")
        self._tick()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        # верхняя полоса
        top = tk.Frame(self.root, bg=BG_PANEL, height=52)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="◤ " + APP_NAME, font=("Consolas", 16, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(side="left", padx=14)
        tk.Label(top, text=BUILD, font=("Consolas", 9),
                 fg=DIM, bg=BG_PANEL).pack(side="left", padx=6)
        tk.Label(top, text="СТАТУС: АКТИВЕН", font=("Consolas", 9, "bold"),
                 fg=ACCENT2, bg=BG_PANEL).pack(side="right", padx=14)
        tk.Label(top, textvariable=self.fps_var, font=FONT,
                 fg=DIM, bg=BG_PANEL).pack(side="right")

        # тело: слева навигация, справа контент
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=12)

        nav = tk.Frame(body, bg=BG_NAV, width=170)
        nav.pack(side="left", fill="y")
        nav.pack_propagate(False)

        self.tabs = ["COMBAT", "RENDER", "MOVEMENT"]
        self.nav_buttons = {}
        for i, name in enumerate(self.tabs):
            b = tk.Button(nav, text=f"  {name}",
                          font=("Consolas", 11, "bold"),
                          bd=0, anchor="w", pady=14,
                          bg=BG_NAV, fg=TXT, activebackground=BG_PANEL,
                          activeforeground=ACCENT,
                          command=lambda n=name: self._show_tab(n))
            b.pack(fill="x", padx=6, pady=2)
            self.nav_buttons[name] = b

        # блок под навигацией (водяной знак)
        foot = tk.Frame(nav, bg=BG_NAV)
        foot.pack(side="bottom", fill="x", pady=8)
        tk.Label(foot, text="guaranteed loss™", font=("Consolas", 8),
                 fg=DIM, bg=BG_NAV).pack()

        self.content = tk.Frame(body, bg=BG_PANEL)
        self.content.pack(side="right", fill="both", expand=True)

        # консоль
        console_frame = tk.Frame(self.root, bg=BG)
        console_frame.pack(fill="both", expand=False, padx=12, pady=(0, 12))
        tk.Label(console_frame, text="СИСТЕМНАЯ КОНСОЛЬ", font=("Consolas", 9, "bold"),
                 fg=DIM, bg=BG).pack(anchor="w")
        self.console = tk.Text(console_frame, height=9, bg="#07090d",
                               fg=ACCENT, font=("Consolas", 9), bd=0,
                               insertbackground=ACCENT, wrap="word",
                               state="disabled", relief="flat")
        self.console.pack(fill="both", expand=True)
        self.console.tag_configure("warn", foreground=ACCENT2)
        self.console.tag_configure("info", foreground=TXT)

        self._show_tab("COMBAT")

    def _content_clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    def _header(self, title, sub):
        tk.Label(self.content, text=title, font=("Consolas", 14, "bold"),
                 fg=ACCENT, bg=BG_PANEL).pack(anchor="w", padx=16, pady=(14, 0))
        tk.Label(self.content, text=sub, font=("Consolas", 9),
                 fg=DIM, bg=BG_PANEL).pack(anchor="w", padx=16, pady=(0, 8))
        tk.Frame(self.content, bg=LINE, height=1).pack(fill="x", padx=16, pady=4)

    def _toggle(self, label, desc, var, on_change=None, danger=False):
        f = tk.Frame(self.content, bg=BG_PANEL)
        f.pack(fill="x", padx=16, pady=8)
        cb = tk.Checkbutton(f, variable=var, bg=BG_PANEL, bd=0,
                            selectcolor=BG_PANEL,
                            activebackground=BG_PANEL,
                            activeforeground=TXT,
                            font=("Consolas", 11, "bold"),
                            fg=(ACCENT2 if danger else TXT),
                            command=on_change)
        cb.pack(side="left")
        d = tk.Frame(f, bg=BG_PANEL)
        d.pack(side="left", padx=6)
        tk.Label(d, text=label, font=("Consolas", 11, "bold"),
                 fg=(ACCENT2 if danger else TXT), bg=BG_PANEL).pack(anchor="w")
        tk.Label(d, text=desc, font=("Consolas", 9),
                 fg=DIM, bg=BG_PANEL).pack(anchor="w")
        return cb

    # ------------------------------------------------------------------ tabs
    def _show_tab(self, name):
        for n, b in self.nav_buttons.items():
            b.configure(bg=ACCENT if n == name else BG_NAV,
                        fg="#0b0e14" if n == name else TXT)
        self._content_clear()
        if name == "COMBAT":
            self._tab_combat()
        elif name == "RENDER":
            self._tab_render()
        else:
            self._tab_movement()

    def _tab_combat(self):
        self._header("COMBAT", "боевые модули саморазрушения")
        self._toggle("ANTI-AIMBOT",
                     "прицел сам отводится ОТ врагов (гарантия промаха)",
                     self.anti_aimbot,
                     lambda: self._on_aimbot())
        self._toggle("ANTI-AIMLESS",
                     "увидел врага -> камера резко крутится куда-то далеко",
                     self.anti_aimless,
                     lambda: self._on_aimless())
        self._toggle("GAMESENSE",
                     "нельзя включить. выключено = дроп оружия на перезарядке (шанс 20%)",
                     self.gamesense, self._on_gamesense, danger=True)

    def _tab_render(self):
        self._header("RENDER", "визуальные галлюцинации")
        self._toggle("ESP",
                     "показывает 'фейк' позиции врагов там, где их НЕТ",
                     self.esp, lambda: self._on_esp())
        self._toggle("VISUAL RECOIL",
                     "отдача увеличена на +400%. целиться невозможно",
                     self.recoil, lambda: self._on_recoil())

    def _tab_movement(self):
        self._header("MOVEMENT", "контроль движений против тебя")
        self._toggle("ANTI-BHOP",
                     "прыжок заблокирован. попробуй допрыгнуть до миду",
                     self.anti_bhop, lambda: self._on_bhop())

    # ------------------------------------------------------------------ handlers
    def _on_aimbot(self):
        if self.anti_aimbot.get():
            self.log("ANTI-AIMBOT: прицел ОТВЕДЁН от врагов. теперь ты целишься в стену.", "warn")
        else:
            self.log("ANTI-AIMBOT: прицел возвращён... на хедшот тебя.")

    def _on_aimless(self):
        if self.anti_aimless.get():
            self.log("ANTI-AIMLESS: активирован. не смотри на них — они смотрят на тебя.", "warn")
        else:
            self.log("ANTI-AIMLESS: деактивирован. камера больше не разрывается.")

    def _on_gamesense(self):
        # Включить нельзя — мгновенно откатываем в off
        if self.gamesense.get():
            self.gamesense.set(False)
            self.log("GAMESENSE: заблокировано. модуль нельзя включить.", "warn")
        self.log("GAMESENSE: дроп оружия активен на перезарядке (шанс 20%).", "warn")

    def _on_esp(self):
        if self.esp.get():
            self.log("ESP: нарисованы 6 фейк-врагов. вокруг тебя пусто.", "warn")
        else:
            self.log("ESP: фейк-враги убраны. теперь ты по-настоящему один.")

    def _on_recoil(self):
        if self.recoil.get():
            self.log("VISUAL RECOIL: отдача +400%. первый выстрел = в потолок.", "warn")
        else:
            self.log("VISUAL RECOIL: отдача сброшена на обычные ~400% по твоему скилу.")

    def _on_bhop(self):
        if self.anti_bhop.get():
            self.log("ANTI-BHOP: прыжок заблокирован. ПРОБЕЛ ОТКЛЮЧЁН.", "warn")
        else:
            self.log("ANTI-BHOP: прыжок разрешён. ты всё равно не допрыгнешь.")

    # ------------------------------------------------------------------ logging
    def log(self, msg, tag="info"):
        self.console.configure(state="normal")
        self.console.insert("end", f"[{self._ts()}] {msg}\n", tag)
        self.console.see("end")
        self.console.configure(state="disabled")

    def _ts(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    # ------------------------------------------------------------------ simulate
    def _tick(self):
        # фейковый фпс
        self.fps_var.set(f"{random.randint(24, 59)} FPS")
        # случайные "события" из жизни саботажного чита
        r = random.random()
        if r < 0.06 and self.anti_aimless.get():
            self.log("ANTI-AIMLESS: враг замечен → камера выкручена на 180°. ты ничего не видел.", "warn")
        if r < 0.04 and self.esp.get():
            self.log("ESP: враг отрисован за стеной на миду. спойлер: его там нет.")
        if r < 0.05 and self.recoil.get():
            self.log("VISUAL RECOIL: магазин ушёл в небо. попал в самолёт.", "warn")
        if r < 0.04 and self.anti_bhop.get():
            self.log("ANTI-BHOP: нажат ПРОБЕЛ — прыжок проигнорирован.", "warn")
        # gamesense: дроп оружия на перезарядке, шанс 20%
        if r < 0.08 and not self.gamesense.get():
            if random.random() < 0.20:
                self.log("GAMESENSE: ПЕРЕЗАРЯДКА → оружие выпало из рук. шанс сработал (20%).", "warn")
            else:
                self.log("GAMESENSE: перезарядка... оружие удержано (остальные 80%).")
        self.root.after(900, self._tick)


def main():
    root = tk.Tk()
    NeverWin(root)
    root.mainloop()


if __name__ == "__main__":
    main()
