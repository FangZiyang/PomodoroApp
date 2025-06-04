import tkinter as tk
from tkinter import ttk
import os
from datetime import datetime
import tkinter.messagebox as msgbox

FLASH_COUNT = 4
FLASH_INTERVAL = 50000

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        root.title("Pomodoro Timer / 番茄钟")

        self.remaining_seconds = 0
        self.is_running = False
        self._flash_job = None
        self._countdown_job = None
        self._flash_state = False
        self._flash_counter = 0
        self._last_plan = ""

        padding = {"padx": 10, "pady": 6}
        root.columnconfigure(0, weight=1)

        # 0. Timer setting
        duration_frame = ttk.Frame(root)
        duration_frame.grid(row=0, column=0, sticky="ew", **padding)
        duration_frame.columnconfigure(1, weight=1)
        ttk.Label(duration_frame, text="Set timer (minutes) / 设置时长（分钟）:").grid(row=0, column=0, sticky="w")
        self.duration_entry = ttk.Entry(duration_frame)
        self.duration_entry.insert(0, "25")
        self.duration_entry.grid(row=0, column=1, sticky="ew")

        # 1. Previous task
        prev_frame = ttk.Frame(root)
        prev_frame.grid(row=1, column=0, sticky="ew", **padding)
        prev_frame.columnconfigure(1, weight=1)
        ttk.Label(prev_frame, text="Previous Task / 上个任务:").grid(row=0, column=0, sticky="w")
        self.prev_label = ttk.Label(prev_frame, text="(none)")
        self.prev_label.grid(row=0, column=1, sticky="ew")

        # 2. Completed
        done_frame = ttk.Frame(root)
        done_frame.grid(row=2, column=0, sticky="ew", **padding)
        done_frame.columnconfigure(1, weight=1)
        ttk.Label(done_frame, text="Completed / 完成内容:").grid(row=0, column=0, sticky="w")
        self.done_entry = ttk.Entry(done_frame)
        self.done_entry.grid(row=0, column=1, sticky="ew")

        # 3. Plan
        plan_frame = ttk.Frame(root)
        plan_frame.grid(row=3, column=0, sticky="ew", **padding)
        plan_frame.columnconfigure(1, weight=1)
        ttk.Label(plan_frame, text="Plan / 当前任务:").grid(row=0, column=0, sticky="w")
        self.plan_entry = ttk.Entry(plan_frame)
        self.plan_entry.grid(row=0, column=1, sticky="ew")

        # 4. Timer display
        timer_frame = ttk.Frame(root)
        timer_frame.grid(row=4, column=0, sticky="ew", **padding)
        self.timer_label = ttk.Label(timer_frame, text="00:00", font=("Helvetica", 64), foreground="blue")
        self.timer_label.pack(fill="x", expand=True)

        # 5. Buttons
        button_frame = ttk.Frame(root)
        button_frame.grid(row=5, column=0, sticky="ew", **padding)
        self.start_button = ttk.Button(button_frame, text="Start / 开始", command=self.start_timer)
        self.start_button.pack(side="left", padx=(0, 5))
        self.reset_button = ttk.Button(button_frame, text="Reset / 重置", command=self.reset_timer, state="disabled")
        self.reset_button.pack(side="left")

        # 6. Topmost toggle
        top_frame = ttk.Frame(root)
        top_frame.grid(row=6, column=0, sticky="w", **padding)
        self.top_var = tk.BooleanVar(value=False)
        self.top_check = ttk.Checkbutton(top_frame, text="Always on Top / 置顶", variable=self.top_var, command=self.toggle_topmost)
        self.top_check.pack(side="left")

        root.resizable(True, True)

    def toggle_topmost(self):
        self.root.wm_attributes("-topmost", self.top_var.get())

    def _format_time(self, seconds: int) -> str:
        m, s = divmod(seconds, 60)
        return f"{m:02d}:{s:02d}"

    def _save_session_to_file(self):
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        date_str = now.strftime("%Y-%m-%d")
        filename = f"pomodoro_log_{date_str}.txt"

        plan = self._last_plan
        completed = self.done_entry.get().strip()
        content = f"=== Pomodoro Session Ended: {timestamp} ===\n"
        content += f"Planned Task / 计划任务: {plan}\n"
        content += f"Completed / 实际完成: {completed or '(未填写)'}\n\n"

        try:
            with open(filename, "a", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print("Error saving session log:", e)

    def start_timer(self):
        if self.is_running:
            return


        if self._flash_job:
            self.root.after_cancel(self._flash_job)
            self._flash_job = None
            self.root.config(background="")
            self._flash_state = False
            self._flash_counter = 0


        self._last_plan = self.plan_entry.get().strip() or "(no task entered)"
        self.plan_entry.config(state="disabled")
        self.duration_entry.config(state="disabled")
        self.done_entry.delete(0, tk.END)

        try:
            minutes = int(self.duration_entry.get())
            if minutes <= 0:
                raise ValueError
        except ValueError:
            minutes = 25

        self.remaining_seconds = minutes * 60
        self.timer_label.config(text=self._format_time(self.remaining_seconds))
        self.is_running = True
        self.start_button.config(state="disabled")
        self.reset_button.config(state="normal")

        self._countdown()

    def _countdown(self):
        if not self.is_running:
            return
        if self.remaining_seconds > 0:
            self.timer_label.config(text=self._format_time(self.remaining_seconds))
            self.remaining_seconds -= 1
            self._countdown_job = self.root.after(1000, self._countdown)
        else:
            self.timer_label.config(text="00:00")
            self._on_timer_end()

    def _on_timer_end(self):
        self.is_running = False
        self.start_button.config(state="normal")
        self.reset_button.config(state="disabled")
        self.plan_entry.config(state="normal")
        self.duration_entry.config(state="normal")
        self.prev_label.config(text=self._last_plan)
        self._flash_counter = 0
        self._flash_state = False
        # self._flash_red()
        self._save_session_to_file()
        msgbox.showinfo("Time's up / 时间到", "⏰ 当前番茄时间已结束！请休息一下或开始下一轮任务。")


    def _flash_red(self):
        if self._flash_counter >= FLASH_COUNT:
            self.root.config(background="")
            self._flash_job = None
            return

            # Alternate red and normal
        if not self._flash_state:
            self.root.config(background="red")
        else:
            self.root.config(background="")

        self._flash_state = not self._flash_state
        if not self._flash_state:
            self._flash_counter += 1

        self._flash_job = self.root.after(FLASH_INTERVAL, self._flash_red)

    def reset_timer(self):
        if self._countdown_job:
            self.root.after_cancel(self._countdown_job)
            self._countdown_job = None
        if self._flash_job:
            self.root.after_cancel(self._flash_job)
            self._flash_job = None
        self.is_running = False
        self.remaining_seconds = 0
        self.timer_label.config(text="00:00")
        self.start_button.config(state="normal")
        self.reset_button.config(state="disabled")
        self.plan_entry.config(state="normal")
        self.duration_entry.config(state="normal")
        self.root.config(background="")

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
