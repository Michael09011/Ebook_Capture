import os
import subprocess
import threading
import time
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText


class EbookCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ebook Capture")
        self.root.geometry("500x660")
        self.root.resizable(False, False)
        self.root.configure(bg="#14152a")

        self.running = False
        self.paused = False
        self.current_page = 0
        self.thread = None

        self._build_ui()

    def _build_ui(self):
        BG = "#14152a"
        CARD = "#1d2240"
        ACCENT = "#0e4c8b"
        HL = "#f25f5c"
        FG = "#f7f7ff"
        MUTED = "#a0a8d8"

        self.root.option_add("*Font", "Helvetica 11")
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Accent.TButton",
                        font=("Helvetica", 11, "bold"),
                        foreground=FG,
                        background=HL,
                        borderwidth=0,
                        focusthickness=3,
                        focuscolor=HL)
        style.map("Accent.TButton",
                  background=[("active", "#ff7b7a"), ("disabled", "#555577")])
        style.configure("Secondary.TButton",
                        foreground=FG,
                        background=ACCENT)
        style.map("Secondary.TButton",
                  background=[("active", "#1a5fa5")])
        style.configure("Danger.TButton",
                        foreground=FG,
                        background="#34395b")
        style.map("Danger.TButton",
                  background=[("active", "#4a4f74")])
        style.configure("Card.TFrame", background=CARD)
        style.configure("Card.TLabel", background=CARD, foreground=FG)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("Header.TLabel", background=BG, foreground=HL, font=("Helvetica", 22, "bold"))
        style.configure("Subheader.TLabel", background=BG, foreground=FG, font=("Helvetica", 11))
        style.configure("TLabel", background=BG, foreground=FG)
        style.configure("TEntry", fieldbackground="#263153", foreground=FG, background="#263153")
        style.configure("TSeparator", background="#2f365b")
        style.configure("TProgressbar", troughcolor="#1d2240", background=HL, thickness=12)

        header = ttk.Frame(self.root, style="Card.TFrame", padding=(20, 18))
        header.pack(fill="x", padx=20, pady=(20, 10))
        ttk.Label(header, text="📚 Ebook Capture", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text="AladinEbook 자동 캡처를 간편하게", style="Subheader.TLabel").pack(anchor="w", pady=(6, 0))

        settings_card = ttk.Frame(self.root, style="Card.TFrame", padding=(20, 18))
        settings_card.pack(fill="x", padx=20, pady=(0, 14))

        def row(label_text, default, var_name, width=26):
            frame = ttk.Frame(settings_card, style="Card.TFrame")
            frame.pack(fill="x", pady=8)
            ttk.Label(frame, text=label_text, width=12, anchor="w", style="Card.TLabel").pack(side="left")
            var = tk.StringVar(value=default)
            setattr(self, var_name, var)
            entry = ttk.Entry(frame, textvariable=var, width=width, style="TEntry")
            entry.pack(side="left", padx=(10, 0), fill="x", expand=True)
            return entry

        row("앱 이름", "AladinEbook", "app_name")
        row("저장 폴더", os.path.expanduser("~/Desktop/ebook/"), "save_folder")
        ttk.Button(settings_card, text="폴더 선택", style="Secondary.TButton", command=self.choose_folder).pack(anchor="e", pady=(4, 6))
        row("총 페이지", "0", "total_pages")
        row("캡처 X", "508", "cap_x")
        row("캡처 Y", "67", "cap_y")
        row("캡처 폭", "672", "cap_w")
        row("캡처 높이", "933", "cap_h")
        ttk.Button(settings_card, text="좌표 선택", style="Secondary.TButton", command=self.select_capture_region).pack(anchor="e", pady=(4, 6))
        row("딜레이(초)", "1.0", "delay_sec")

        separator = ttk.Separator(self.root, orient="horizontal")
        separator.pack(fill="x", padx=20, pady=(0, 16))

        progress_card = ttk.Frame(self.root, style="Card.TFrame", padding=(20, 16))
        progress_card.pack(fill="x", padx=20)
        self.progress_label = ttk.Label(progress_card, text="대기 중...", style="Muted.TLabel")
        self.progress_label.pack(anchor="w")
        self.progress_bar = ttk.Progressbar(progress_card, mode="determinate")
        self.progress_bar.pack(fill="x", pady=(10, 0))
        self.status_label = ttk.Label(progress_card, text="준비됨", style="Muted.TLabel")
        self.status_label.pack(anchor="w", pady=(10, 0))

        btn_frame = ttk.Frame(self.root, style="Card.TFrame")
        btn_frame.pack(fill="x", padx=20, pady=18)
        self.start_btn = ttk.Button(btn_frame, text="▶ 시작", style="Accent.TButton", command=self.start)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=5)
        self.pause_btn = ttk.Button(btn_frame, text="⏸ 일시정지", style="Secondary.TButton", command=self.toggle_pause, state="disabled")
        self.pause_btn.pack(side="left", expand=True, fill="x", padx=5)
        self.stop_btn = ttk.Button(btn_frame, text="■ 중지", style="Danger.TButton", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=5)

        log_card = ttk.Frame(self.root, style="Card.TFrame", padding=(20, 18))
        log_card.pack(fill="both", padx=20, pady=(0, 20), expand=True)
        ttk.Label(log_card, text="실행 로그", style="Card.TLabel").pack(anchor="w")
        self.log_text = ScrolledText(log_card, height=9, bg="#1e2548", fg=FG, insertbackground=FG, relief="flat", wrap="word")
        self.log_text.pack(fill="both", expand=True, pady=(10, 0))
        self.log_text.configure(state="disabled")

    def choose_folder(self):
        folder = filedialog.askdirectory(
            initialdir=self.save_folder.get() or os.path.expanduser("~"),
            title="저장 폴더 선택"
        )
        if folder:
            self.save_folder.set(folder)

    def select_capture_region(self):
        self.log("마우스로 캡처 영역을 선택하세요.")
        overlay = tk.Toplevel(self.root)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-alpha", 0.22)
        overlay.attributes("-topmost", True)
        overlay.configure(bg="black")
        overlay.grab_set()

        canvas = tk.Canvas(overlay, cursor="cross", bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        selection = {"start_x": 0, "start_y": 0, "rect": None}

        def on_press(event):
            selection["start_x"] = event.x_root
            selection["start_y"] = event.y_root
            selection["rect"] = canvas.create_rectangle(
                selection["start_x"], selection["start_y"],
                selection["start_x"], selection["start_y"],
                outline="#f25f5c", width=2
            )

        def on_drag(event):
            if selection["rect"] is None:
                return
            canvas.coords(selection["rect"],
                          selection["start_x"], selection["start_y"],
                          event.x_root, event.y_root)

        def on_release(event):
            if selection["rect"] is None:
                return
            x0 = min(selection["start_x"], event.x_root)
            y0 = min(selection["start_y"], event.y_root)
            x1 = max(selection["start_x"], event.x_root)
            y1 = max(selection["start_y"], event.y_root)
            w = x1 - x0
            h = y1 - y0
            overlay.grab_release()
            overlay.destroy()
            if w > 0 and h > 0:
                self.cap_x.set(str(int(x0)))
                self.cap_y.set(str(int(y0)))
                self.cap_w.set(str(int(w)))
                self.cap_h.set(str(int(h)))
                self.log(f"선택 완료: {x0},{y0},{w},{h}")
            else:
                self.log("캡처 영역 선택이 취소되었습니다.")

        def cancel_selection(event=None):
            overlay.grab_release()
            overlay.destroy()
            self.log("캡처 영역 선택 취소")

        canvas.bind("<ButtonPress-1>", on_press)
        canvas.bind("<B1-Motion>", on_drag)
        canvas.bind("<ButtonRelease-1>", on_release)
        overlay.bind("<Escape>", cancel_selection)
        overlay.focus_set()

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    def start(self):
        try:
            total = int(self.total_pages.get())
            float(self.delay_sec.get())
        except ValueError:
            messagebox.showwarning("입력 오류", "숫자 입력값을 확인하세요.")
            return

        if total <= 0:
            messagebox.showwarning("입력 오류", "총 페이지 수를 1 이상으로 입력하세요.")
            return

        folder = self.save_folder.get().strip()
        if not folder:
            messagebox.showwarning("입력 오류", "저장 폴더를 선택해주세요.")
            return

        os.makedirs(folder, exist_ok=True)
        self.running = True
        self.paused = False
        self.current_page = 0
        self.progress_bar["maximum"] = total
        self.progress_bar["value"] = 0
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.status_label.config(text="캡처 시작", foreground="#a8d3ff")

        self.thread = threading.Thread(target=self.capture_loop, daemon=True)
        self.thread.start()

    def capture_loop(self):
        app = self.app_name.get().strip()
        folder = self.save_folder.get().strip()
        total = int(self.total_pages.get())
        x = self.cap_x.get().strip()
        y = self.cap_y.get().strip()
        w = self.cap_w.get().strip()
        h = self.cap_h.get().strip()
        delay = float(self.delay_sec.get())

        subprocess.run(["osascript", "-e", f'tell application "{app}" to activate'])
        time.sleep(2)
        self.log(f"{app} 활성화 완료")

        for i in range(total):
            if not self.running:
                break
            while self.paused:
                time.sleep(0.2)

            self.current_page = i + 1
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            fname = f"ebook_{i+1:04d}_{ts}.png"
            fpath = os.path.join(folder, fname)
            subprocess.run(["screencapture", "-R", f"{x},{y},{w},{h}", fpath])
            time.sleep(0.3)

            applescript = (
                'tell application "System Events"\n'
                '    tell process "{app}"\n'
                '        key code 124\n'
                '    end tell\n'
                'end tell'
            ).format(app=app)
            subprocess.run(["osascript", "-e", applescript])
            if self.current_page % 20 == 0:
                subprocess.run(["cliclick", "m:200,500", "m:210,510", "m:200,500"], capture_output=True)
                self.log(f"[{self.current_page}/{total}] 마우스 흔들기")

            self.root.after(0, self.update_progress, self.current_page, total)
            time.sleep(delay)

        if self.running:
            self.root.after(0, self.done)

    def update_progress(self, current, total):
        self.progress_bar["value"] = current
        self.progress_label.config(text=f"{current} / {total} 페이지 ({current / total * 100:.1f}%)")
        self.status_label.config(text=f"진행 중: {current}/{total}")
        if current % 10 == 0:
            self.log(f"[{current}/{total}] 캡처 중...")

    def done(self):
        self.running = False
        self.progress_label.config(text="✅ 완료!")
        self.status_label.config(text="작업이 완료되었습니다.", foreground="#7fff7f")
        self.log("캡처 완료!")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        subprocess.run(["osascript", "-e",
                        'display notification "캡처 완료!" with title "Ebook Capture" sound name "Glass"'])

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ 재개")
            self.status_label.config(text="일시정지 중", foreground="#ffc46b")
            self.log("일시정지")
        else:
            self.pause_btn.config(text="⏸ 일시정지")
            self.status_label.config(text="캡처 재개", foreground="#a8d3ff")
            self.log("재개")

    def stop(self):
        self.running = False
        self.paused = False
        self.progress_label.config(text="중지됨")
        self.status_label.config(text="작업이 중지되었습니다.", foreground="#ff7b7b")
        self.log(f"중지 (총 {self.current_page}페이지 캡처)")
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = EbookCaptureApp(root)
    root.mainloop()
