import os, sys, shutil, tempfile, hashlib, json, subprocess
from pathlib import Path
import requests

# ---------------- UPDATE LOGIC ----------------
LOCAL_VERSION_FILE = "VERSION"
REMOTE_META_URL = "https://raw.githubusercontent.com/Tropikanogr/float_widget/main/version.json"

def read_local_version():
    try:
        return Path(LOCAL_VERSION_FILE).read_text(encoding="utf-8").strip()
    except Exception:
        return "0.0.0"

def write_local_version(v: str):
    Path(LOCAL_VERSION_FILE).write_text(v, encoding="utf-8")

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*256), b""):
            h.update(chunk)
    return h.hexdigest()

def fetch_remote_meta() -> dict:
    r = requests.get(REMOTE_META_URL, timeout=20)
    r.raise_for_status()
    return r.json()

def self_update():
    local_v = read_local_version()
    print(f"🔎 Local version: {local_v}")

    try:
        meta = fetch_remote_meta()
    except Exception as e:
        print("⚠️ Cannot fetch version info:", e)
        return

    remote_v = str(meta.get("version", "0.0.0"))
    url = meta.get("url")
    expect_sha = str(meta.get("sha256", "")).lower()
    print(f"🌐 Remote version: {remote_v}")

    if not url or remote_v <= local_v:
        print("✅ Already up to date")
        return

    print(f"⬇️ Downloading {remote_v} …")
    tmpdir = Path(tempfile.mkdtemp())
    tmpfile = tmpdir / "update.exe"
    try:
        with requests.get(url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(tmpfile, "wb") as f:
                for chunk in r.iter_content(1024 * 64):
                    if chunk:
                        f.write(chunk)

        if expect_sha:
            actual = sha256_file(tmpfile).lower()
            if actual != expect_sha:
                raise RuntimeError(f"Checksum mismatch! expected {expect_sha} got {actual}")

        # Πού βρίσκεται το τρέχον executable ή script
        if getattr(sys, "frozen", False):
            exe_path = Path(sys.executable).resolve()
        else:
            # αν τρέχεις από python script (dev mode), απλά κάνε replace το script’s exe-στόχο (προαιρετικό)
            exe_path = Path(sys.argv[0]).resolve()

        backup = exe_path.with_suffix(".old.exe")
        bat    = exe_path.with_suffix(".update.bat")
        version_file = exe_path.with_name("VERSION")

        # .bat που θα τρέξει ΑΦΟΥ κλείσει η τρέχουσα διεργασία
        bat_content = f"""@echo off
setlocal
REM μικρή αναμονή να τερματίσει το παλιό exe
ping 127.0.0.1 -n 2 >nul
if exist "{backup}" del /f /q "{backup}" >nul
copy /y "{exe_path}" "{backup}" >nul
copy /y "{tmpfile}" "{exe_path}" >nul
> "{version_file}" echo {remote_v}
start "" "{exe_path}"
del /f /q "%~f0"
"""

        bat.write_text(bat_content, encoding="utf-8")
        print("✅ Updated, restarting…")
        # τρέξε το .bat και βγες για να ελευθερωθεί το αρχείο
        subprocess.Popen(['cmd', '/c', str(bat)], close_fds=True)
        sys.exit(0)

    except Exception as e:
        print("❌ Update failed:", e)







import tkinter as tk
from tkinter import Menu, messagebox
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys
import threading
import requests
from bs4 import BeautifulSoup

# Windows-only sound (optional)
try:
    import winsound
except Exception:
    winsound = None

# Text-to-speech for voice notifications
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    pyttsx3 = None

BG = "#121212"; FG = "#FFFFFF"
ACCENT_OPEN = "#00D26A"   # RTH
ACCENT_PRE  = "#E0B300"   # Pre
ACCENT_AFTER= "#1EA7FD"   # After
ACCENT_OFF  = "#B19CD9"   # Closed
TIME_GR = "#FF6B6B"       # Greece (red)
TIME_NY = "#4ECDC4"       # New York (cyan)
FONT = ("Segoe UI", 12, "bold")
REFRESH_MS = 200

TZ_GR = ZoneInfo("Europe/Athens")
TZ_NY = ZoneInfo("America/New_York")

# NYSE hours (ET). Holidays not included.
PRE_START  = (4,  0)
OPEN_TIME  = (9, 30)
CLOSE_TIME = (16, 0)
AFTER_END  = (20, 0)

def today_dt(ny_now, hhmm):
    h,m = hhmm
    return ny_now.replace(hour=h, minute=m, second=0, microsecond=0)

def next_business_day_0400(ny_now):
    d = ny_now
    add = 1
    while True:
        d = (ny_now + timedelta(days=add)).replace(hour=4, minute=0, second=0, microsecond=0)
        if d.weekday() < 5:
            return d
        add += 1

def session_info(ny_now: datetime):
    """Returns (phase, phase_color, next_events: list[(label, dt)], dot_on)"""
    if ny_now.weekday() >= 5:
        nxt = next_business_day_0400(ny_now)
        return ("CLOSED", ACCENT_OFF, [("Pre", nxt)], False)

    pre_start  = today_dt(ny_now, PRE_START)
    open_time  = today_dt(ny_now, OPEN_TIME)
    close_time = today_dt(ny_now, CLOSE_TIME)
    after_end  = today_dt(ny_now, AFTER_END)

    if ny_now < pre_start:
        return ("CLOSED", ACCENT_OFF, [("Pre", pre_start), ("Open", open_time)], False)
    if pre_start <= ny_now < open_time:
        return ("PRE", ACCENT_PRE, [("Open", open_time), ("Close", close_time)], True)
    if open_time <= ny_now < close_time:
        return ("RTH", ACCENT_OPEN, [("Close", close_time), ("A/H End", after_end)], True)
    if close_time <= ny_now < after_end:
        return ("AFTER", ACCENT_AFTER, [("A/H End", after_end), ("Pre", next_business_day_0400(ny_now))], True)

    return ("CLOSED", ACCENT_OFF, [
        ("Pre", next_business_day_0400(ny_now)),
        ("Open", next_business_day_0400(ny_now).replace(hour=9, minute=30))
    ], False)

def fmt_delta(td: timedelta):
    if td.total_seconds() < 0: td = -td
    h = int(td.total_seconds()//3600)
    m = int((td.total_seconds()%3600)//60)
    s = int(td.total_seconds()%60)
    if h > 99: h = 99
    return f"{h:02d}:{m:02d}:{s:02d}"

class FloatClock(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Float_Clock")
        self.configure(bg=BG)
        self.overrideredirect(True)
        self.wm_attributes("-topmost", True)
        self.wm_attributes("-alpha", 0.94)

        self.compact = True
        self.sound_enabled = True
        self.voice_enabled = True
        self.last_phase = None

        # Tkinter vars for menu checkbuttons
        self.sound_var = tk.BooleanVar(value=self.sound_enabled)
        self.voice_var = tk.BooleanVar(value=self.voice_enabled)

        # UI
        self.wrap = tk.Frame(self, bg=BG)
        self.wrap.pack(padx=10, pady=8)

        # Clock section
        self.clock_frame = tk.Frame(self.wrap, bg=BG)
        self.clock_frame.pack(fill="x", pady=(0, 10))

        self.time_gr = tk.Label(self.clock_frame, text="", fg=TIME_GR, bg=BG, font=FONT)
        self.time_ny = tk.Label(self.clock_frame, text="", fg=TIME_NY, bg=BG, font=FONT)
        self.separator1 = tk.Label(self.clock_frame, text="|", fg=FG, bg=BG, font=FONT)
        self.separator2 = tk.Label(self.clock_frame, text="|", fg=FG, bg=BG, font=FONT)
        self.phase_info = tk.Label(self.clock_frame, text="", fg=FG, bg=BG, font=FONT)
        self.line_sub  = tk.Label(self.clock_frame, text="", fg=FG, bg=BG, font=("Segoe UI", 10))
        self.dot       = tk.Label(self.clock_frame, text="●", fg=ACCENT_OFF, bg=BG, font=("Segoe UI", 10, "bold"))

        self.time_gr.grid(row=0, column=0, sticky="w")
        self.separator1.grid(row=0, column=1, sticky="w", padx=(8,8))
        self.time_ny.grid(row=0, column=2, sticky="w")
        self.separator2.grid(row=0, column=3, sticky="w", padx=(8,8))
        self.phase_info.grid(row=0, column=4, sticky="w")
        self.dot.grid(row=0, column=5, sticky="w", padx=(8,0))
        self.line_sub.grid(row=1, column=0, columnspan=6, sticky="w")

        # Separator line
        self.sep_line = tk.Frame(self.wrap, height=2, bg="#333333")
        self.sep_line.pack(fill="x", pady=5)

        # Float widget section
        self.float_frame = tk.Frame(self.wrap, bg=BG)
        self.float_frame.pack(fill="x")

        self.entry = tk.Entry(self.float_frame, font=("Arial", 12), width=14,
                              bg="#222222", fg=FG, insertbackground=FG)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self.get_data)

        self.btn = tk.Button(self.float_frame, text="Αναζήτηση", command=self.get_data,
                           bg="#333333", fg=FG, activebackground="#444444", activeforeground=FG,
                           relief="flat", bd=0)
        self.btn.pack(pady=5)

        self.update_btn = tk.Button(self.float_frame, text="🔄 Update", command=self.update_app,
                           bg="#444444", fg=FG, activebackground="#555555", activeforeground=FG,
                           relief="flat", bd=0)
        self.update_btn.pack(pady=5)

        self.result_var = tk.StringVar()
        self.result = tk.Label(self.float_frame, textvariable=self.result_var,
                              font=("Arial", 9), wraplength=300, justify="left",
                              bg=BG, fg=FG)
        self.result.pack(pady=5)

        # Drag only για labels/frames (όχι Entry/Buttons)
        for w in (self, self.wrap, self.clock_frame, self.float_frame,
                  self.time_gr, self.time_ny, self.separator1, self.separator2,
                  self.phase_info, self.line_sub, self.dot, self.result):
            w.bind("<ButtonPress-1>", self.start_move)
            w.bind("<B1-Motion>", self.do_move)
            w.bind("<Button-3>", self.show_menu)

        self.build_menu()
        self.position_initial()
        self.update_clock()

    def position_initial(self):
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        ww, wh = self.winfo_reqwidth(), self.winfo_reqheight()
        self.geometry(f"+{max(0, sw - ww - 32)}+{max(0, sh - wh - 64)}")

    def start_move(self, e):
        # αν το widget είναι Entry ή Button, αγνόησε το drag
        if isinstance(e.widget, (tk.Entry, tk.Button)):
            return
        self._x, self._y = e.x, e.y

    def do_move(self, e):
        # επίσης skip αν ξεκίνησε από Entry/Button
        if isinstance(e.widget, (tk.Entry, tk.Button)):
            return
        self.geometry(f"+{e.x_root - self._x}+{e.y_root - self._y}")


    def build_menu(self):
        m = Menu(self, tearoff=0, bg="#222", fg="#ddd",
                 activebackground="#333", activeforeground="#fff")
        m.add_command(label="Toggle compact", command=self.toggle_compact)
        m.add_separator()
        m.add_command(label="Opacity 100%", command=lambda: self.set_alpha(1.0))
        m.add_command(label="Opacity 85%", command=lambda: self.set_alpha(0.85))
        m.add_command(label="Opacity 70%", command=lambda: self.set_alpha(0.70))
        m.add_separator()
        m.add_checkbutton(label="Sound on phase change", variable=self.sound_var,
                          onvalue=True, offvalue=False, command=self.toggle_sound)
        m.add_checkbutton(label="Voice notifications", variable=self.voice_var,
                          onvalue=True, offvalue=False, command=self.toggle_voice)
        m.add_separator()
        m.add_command(label="Copy times", command=self.copy_times)
        m.add_command(label="Quit", command=self.force_exit)

        self.menu = m

    def toggle_sound(self):
        self.sound_enabled = self.sound_var.get()

    def toggle_voice(self):
        self.voice_enabled = self.voice_var.get()

    def set_alpha(self, v): self.wm_attributes("-alpha", v)

    def toggle_compact(self):
        self.compact = not self.compact
        if self.compact:
            self.line_sub.grid_remove()
        else:
            self.line_sub.grid()

    def show_menu(self, e):
        try: self.menu.tk_popup(e.x_root, e.y_root)
        finally: self.menu.grab_release()

    def copy_times(self):
        now_gr = datetime.now(TZ_GR).strftime("%Y-%m-%d %H:%M:%S")
        now_ny = datetime.now(TZ_NY).strftime("%Y-%m-%d %H:%M:%S")
        txt = f"GR  {now_gr}\nNYC {now_ny}"
        self.clipboard_clear()
        self.clipboard_append(txt)

    def beep(self):
        if not self.sound_enabled or winsound is None: return
        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

    def speak_phase(self, phase):
        if not self.voice_enabled or not TTS_AVAILABLE:
            return
        msgs = {
            "PRE": "Pre Market Open",
            "RTH": "Market Open",
            "AFTER": "After Market Open",
            "CLOSED": "Market Closed"
        }
        message = msgs.get(phase, phase)
        def speak_in_thread():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.8)
                engine.say(message)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"TTS Error: {e}")
        threading.Thread(target=speak_in_thread, daemon=True).start()

    def get_data(self, event=None):
        ticker = self.entry.get().upper()
        if not ticker:
            self.result_var.set("Please enter a ticker symbol")
            return
        url = f"https://finviz.com/quote.ashx?t={ticker}"
        headers = {"User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=8)
            soup = BeautifulSoup(response.content, "html.parser")
            data = {}
            for row in soup.select(".snapshot-table2 tr"):
                cells = row.find_all("td")
                for i in range(0, len(cells) - 1, 2):
                    key = cells[i].text.strip()
                    value = cells[i + 1].text.strip()
                    data[key] = value

            float_val = data.get("Shs Float", "N/A")
            vol_val = data.get("Volume", "N/A")
            short_float = data.get("Short Float", "N/A")
            short_ratio = data.get("Short Ratio", "N/A")
            high_52w = data.get("52W High", "N/A")
            low_52w = data.get("52W Low", "N/A")

            # Country από το profile box (τελευταία γραμμή)
            country = "N/A"
            profile_box = soup.select_one(".fullview-profile")
            if profile_box:
                lines = list(profile_box.stripped_strings)
                if lines:
                    country = lines[-1]

            result_text = (
                f"Float: {float_val} | Volume: {vol_val}\n"
                f"Short Float: {short_float} | Short Ratio: {short_ratio}\n"
                f"52W High: {high_52w} | 52W Low: {low_52w}\n"
                f"Country: {country}"
            )
            self.result_var.set(result_text)
        except Exception:
            self.result_var.set("Σφάλμα ανάκτησης")

    def update_clock(self):
        try:
            now_gr = datetime.now(TZ_GR)
            now_ny = datetime.now(TZ_NY)
            phase, color, milestones, dot_on = session_info(now_ny)
            if phase != self.last_phase and self.last_phase is not None:
                self.beep()
                self.speak_phase(phase)
            self.last_phase = phase
            t_gr = now_gr.strftime("GR  %H:%M:%S")
            t_ny = now_ny.strftime("NYC %H:%M:%S")
            self.time_gr.configure(text=t_gr)
            self.time_ny.configure(text=t_ny)
            self.dot.configure(fg=color)
            if self.compact:
                if len(milestones) >= 2:
                    left1 = fmt_delta(milestones[0][1] - now_ny)
                    left2 = fmt_delta(milestones[1][1] - now_ny)
                    self.phase_info.configure(
                        text=f"{phase}  {left1}→{milestones[0][0]}  ·  {left2}→{milestones[1][0]}"
                    )
                else:
                    left1 = fmt_delta(milestones[0][1] - now_ny)
                    self.phase_info.configure(text=f"{phase}  {left1}→{milestones[0][0]}")
            else:
                self.phase_info.configure(text=phase)
                sub = [f"{fmt_delta(when_dt - now_ny)}→{label}" for label, when_dt in milestones[:2]]
                self.line_sub.configure(text="  ·  ".join(sub))
        except Exception as e:
            self.phase_info.configure(text=f"Error: {e}")
        self.after(REFRESH_MS, self.update_clock)

    def update_app(self):
        self.result_var.set("🔄 Checking for update...")
        self.update_idletasks()
        self_update()
        self.result_var.set("✅ Update check complete")

    def force_exit(self):
        self.destroy()
        sys.exit(0)


if __name__ == "__main__":
    try:
        self_update()
        app = FloatClock()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        sys.exit(1)
