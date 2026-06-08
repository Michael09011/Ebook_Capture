import tkinter as tk
from tkinter import ttk, filedialog
import subprocess
import threading
import os
import sys

def ensure_img2pdf():
    try:
        import img2pdf
        return True
    except ImportError:
        return False

class Png2PdfApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG → PDF 변환기")
        self.root.geometry("500x580")
        self.root.resizable(False, False)

        self.BG    = "#0d1117"
        self.CARD  = "#161b22"
        self.ACCENT= "#21262d"
        self.HL    = "#58a6ff"
        self.FG    = "#e6edf3"
        self.MUTED = "#6e7681"
        self.GREEN = "#3fb950"
        self.RED   = "#f85149"

        self.root.configure(bg=self.BG)
        self.folder_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.running = False
        self.png_files = []

        self._build_ui()
        self._check_img2pdf()

    def _check_img2pdf(self):
        if not ensure_img2pdf():
            self.log("img2pdf 없음 → 자동 설치 중...")
            threading.Thread(target=self._install_img2pdf, daemon=True).start()
        else:
            self.log("img2pdf 준비 완료 ✓")

    def _install_img2pdf(self):
        subprocess.run([sys.executable, "-m", "pip", "install", "img2pdf"], capture_output=True)
        self.root.after(0, lambda: self.log("img2pdf 설치 완료 ✓"))

    def _build_ui(self):
        BG=self.BG; CARD=self.CARD; ACCENT=self.ACCENT
        HL=self.HL; FG=self.FG; MUTED=self.MUTED

        tk.Label(self.root, text="PNG → PDF", font=("Helvetica", 24, "bold"),
                 bg=BG, fg=HL).pack(pady=(24, 2))
        tk.Label(self.root, text="이미지 폴더를 선택하고 PDF로 변환하세요",
                 font=("Helvetica", 11), bg=BG, fg=MUTED).pack(pady=(0, 20))

        card = tk.Frame(self.root, bg=CARD, padx=20, pady=16)
        card.pack(fill="x", padx=24)

        tk.Label(card, text="PNG 폴더", font=("Helvetica", 11, "bold"), bg=CARD, fg=FG).pack(anchor="w")
        f1 = tk.Frame(card, bg=CARD)
        f1.pack(fill="x", pady=(4, 10))
        tk.Entry(f1, textvariable=self.folder_path, font=("Helvetica", 11),
                 bg=ACCENT, fg=FG, insertbackground=FG, relief="flat", width=32).pack(side="left")
        tk.Button(f1, text="찾기", font=("Helvetica", 10), bg=HL, fg="white",
                  relief="flat", padx=8, command=self.select_folder).pack(side="left", padx=(6,0))

        tk.Label(card, text="저장 경로 (PDF)", font=("Helvetica", 11, "bold"), bg=CARD, fg=FG).pack(anchor="w")
        f2 = tk.Frame(card, bg=CARD)
        f2.pack(fill="x", pady=(4, 0))
        tk.Entry(f2, textvariable=self.output_path, font=("Helvetica", 11),
                 bg=ACCENT, fg=FG, insertbackground=FG, relief="flat", width=32).pack(side="left")
        tk.Button(f2, text="찾기", font=("Helvetica", 10), bg=HL, fg="white",
                  relief="flat", padx=8, command=self.select_output).pack(side="left", padx=(6,0))

        list_frame = tk.Frame(self.root, bg=BG)
        list_frame.pack(fill="x", padx=24, pady=(14, 0))

        self.file_count_label = tk.Label(list_frame, text="파일 없음",
                                          font=("Helvetica", 11), bg=BG, fg=MUTED)
        self.file_count_label.pack(anchor="w")

        lb_frame = tk.Frame(list_frame, bg=CARD)
        lb_frame.pack(fill="x", pady=(4, 0))
        sb = tk.Scrollbar(lb_frame)
        sb.pack(side="right", fill="y")
        self.listbox = tk.Listbox(lb_frame, height=7, font=("Menlo", 10),
                                   bg=CARD, fg=MUTED, relief="flat",
                                   selectbackground=ACCENT, yscrollcommand=sb.set,
                                   borderwidth=0, highlightthickness=0)
        self.listbox.pack(fill="x")
        sb.config(command=self.listbox.yview)

        prog_frame = tk.Frame(self.root, bg=BG)
        prog_frame.pack(fill="x", padx=24, pady=(14, 0))

        self.progress_label = tk.Label(prog_frame, text="대기 중...",
                                        font=("Helvetica", 11), bg=BG, fg=MUTED)
        self.progress_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(prog_frame, length=450, mode="indeterminate")
        self.progress_bar.pack(fill="x", pady=(4, 0))

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TProgressbar", troughcolor=CARD, background=HL, thickness=12)

        self.convert_btn = tk.Button(self.root, text="▶ PDF 변환 시작",
                                      font=("Helvetica", 13, "bold"),
                                      bg=self.GREEN, fg="white", relief="flat",
                                      padx=20, pady=8, activebackground="#2ea043",
                                      command=self.start_convert)
        self.convert_btn.pack(pady=16)

        log_frame = tk.Frame(self.root, bg=BG)
        log_frame.pack(fill="x", padx=24)
        self.log_text = tk.Text(log_frame, height=4, font=("Menlo", 10),
                                 bg=CARD, fg=MUTED, relief="flat",
                                 state="disabled", wrap="word")
        self.log_text.pack(fill="x")

    def select_folder(self):
        folder = filedialog.askdirectory(title="PNG 폴더 선택")
        if folder:
            self.folder_path.set(folder)
            self.output_path.set(os.path.join(os.path.dirname(folder), "ebook_output.pdf"))
            self.load_files(folder)

    def select_output(self):
        path = filedialog.asksaveasfilename(title="PDF 저장 위치",
                                             defaultextension=".pdf",
                                             filetypes=[("PDF files", "*.pdf")])
        if path:
            self.output_path.set(path)

    def load_files(self, folder):
        files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".png")])
        self.png_files = [os.path.join(folder, f) for f in files]
        self.listbox.delete(0, "end")
        for f in files:
            self.listbox.insert("end", f)
        count = len(files)
        self.file_count_label.config(
            text=f"총 {count}개 PNG 파일 발견",
            fg=self.HL if count > 0 else self.RED)
        self.log(f"폴더 로드 완료: {count}개 파일")

    def start_convert(self):
        if not self.png_files:
            self.log("PNG 파일이 없어요!")
            return
        if not self.output_path.get():
            self.log("저장 경로를 설정하세요!")
            return
        self.running = True
        self.convert_btn.config(state="disabled")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)
        threading.Thread(target=self.convert_loop, daemon=True).start()

    def convert_loop(self):
        import img2pdf
        output = self.output_path.get()
        total = len(self.png_files)
        self.root.after(0, lambda: self.log(f"변환 시작: {total}장 → PDF 하나로 합치는 중..."))
        self.root.after(0, lambda: self.progress_label.config(
            text=f"0 / {total} 처리 중...", fg=self.FG))
        try:
            # img2pdf 단독으로 전체 변환 (외부 라이브러리 불필요)
            with open(output, "wb") as f:
                f.write(img2pdf.convert(self.png_files))
            self.root.after(0, self.done, output)
        except Exception as e:
            self.root.after(0, lambda err=str(e): self.log(f"오류: {err}"))
            self.root.after(0, lambda: self.progress_bar.stop())
            self.root.after(0, lambda: self.convert_btn.config(state="normal"))

    def done(self, output):
        self.running = False
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate")
        self.progress_bar["value"] = 100
        self.progress_bar["maximum"] = 100
        self.progress_label.config(text="✅ 변환 완료!", fg=self.GREEN)
        self.log(f"저장 완료: {output}")
        self.convert_btn.config(state="normal")
        subprocess.run(["osascript", "-e",
            'display notification "PDF 변환 완료!" with title "PNG→PDF" sound name "Glass"'])
        subprocess.run(["open", "-R", output])

    def log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = Png2PdfApp(root)
    root.mainloop()
