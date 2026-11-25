import threading
import time
from tkinter import messagebox
import customtkinter as ctk
import cv2
from PIL import Image
from detection.monitor import Monitor
from database.db_manager import Database
from utils.focus_score import calculate_focus_score
from utils.notifications import notify
from dashboard.analytics import show_analytics, show_saved_sessions

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

APP_BG = ("#F2F5F9", "#111827")
SURFACE = ("#FFFFFF", "#1E293B")
SURFACE_ALT = ("#F7F9FC", "#263449")
VIDEO_BG = ("#172536", "#0B1220")
ACCENT = ("#167D6A", "#34D399")
ACCENT_HOVER = ("#116657", "#10B981")
TEXT = ("#182B3A", "#F8FAFC")
MUTED = ("#647789", "#A6B4C4")
BORDER = ("#DCE4EC", "#334155")
GOOD = ("#167D6A", "#34D399")
WARNING = ("#A15C00", "#FBBF24")
BAD = ("#B42318", "#FDA4AF")
START_TEXT = ("#FFFFFF", "#082F25")
STOP_BG = ("#FDECEC", "#3B2028")
STOP_HOVER = ("#FADADA", "#542B3A")
STOP_BORDER = ("#F2C6C6", "#613541")
GUIDANCE_BG = ("#EAF5F2", "#17352F")
GUIDANCE_BORDER = ("#D4E9E3", "#285244")

class FocusGuardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FocusGuard AI | Focus & Posture Guardian")
        self.geometry("1240x800")
        self.minsize(1050, 700)
        self.configure(fg_color=APP_BG)
        self.db = Database()
        self.monitor = Monitor()
        self.running = False
        self.cap = None
        self.worker = None
        self.started_at = None
        self.last_alert = {}
        self.posture_events = 0
        self.eye_alerts = 0
        self.frames = 0
        self.good_frames = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            self, fg_color=SURFACE, corner_radius=0, height=82,
            border_width=1, border_color=BORDER
        )
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        brand = ctk.CTkFrame(header, fg_color=SURFACE)
        brand.pack(side="left", padx=28, pady=14)
        ctk.CTkLabel(
            brand, text="FG", width=42, height=42, corner_radius=8,
            fg_color=("#DDF2EC", "#164136"), text_color=ACCENT,
            font=ctk.CTkFont(size=17, weight="bold")
        ).pack(side="left", padx=(0, 13))
        brand_text = ctk.CTkFrame(brand, fg_color=SURFACE)
        brand_text.pack(side="left")
        ctk.CTkLabel(
            brand_text, text="FocusGuard AI", text_color=TEXT,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand_text, text="REAL-TIME FOCUS & POSTURE MONITOR",
            text_color=MUTED, font=ctk.CTkFont(size=10)
        ).pack(anchor="w", pady=(1, 0))

        nav = ctk.CTkFrame(header, fg_color=SURFACE)
        nav.pack(side="right", padx=24, pady=16)
        ctk.CTkButton(
            nav, text="Session History", command=self.saved_sessions,
            width=142, height=40, corner_radius=7,
            fg_color=SURFACE, hover_color=SURFACE_ALT, text_color=TEXT,
            border_width=1, border_color=BORDER
        ).pack(side="left", padx=(0, 10))
        ctk.CTkButton(
            nav, text="Analytics", command=self.analytics,
            width=112, height=40, corner_radius=7,
            fg_color=ACCENT, hover_color=ACCENT_HOVER, text_color=START_TEXT
        ).pack(side="left")
        ctk.CTkLabel(
            nav, text="Theme", text_color=MUTED,
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(18, 7))
        self.theme_toggle = ctk.CTkSegmentedButton(
            nav, values=["Light", "Dark"], command=self.change_theme,
            width=138, height=36, corner_radius=6,
            fg_color=SURFACE_ALT, selected_color=("#DDF2EC", "#164136"),
            selected_hover_color=("#CDE9E1", "#205344"),
            unselected_color=SURFACE_ALT, unselected_hover_color=BORDER,
            text_color=TEXT
        )
        self.theme_toggle.pack(side="left")
        self.theme_toggle.set("Light")

        content = ctk.CTkFrame(self, fg_color=APP_BG)
        content.grid(row=1, column=0, sticky="nsew", padx=28, pady=(22, 24))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(1, weight=1)
        intro = ctk.CTkFrame(content, fg_color=APP_BG)
        intro.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        ctk.CTkLabel(
            intro, text="Focus monitoring dashboard", text_color=TEXT,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w")
        ctk.CTkLabel(
            intro, text="Live posture and eye-state feedback, with your session history in one place.",
            text_color=MUTED, font=ctk.CTkFont(size=13)
        ).pack(anchor="w", pady=(4, 0))

        panels = ctk.CTkFrame(content, fg_color=APP_BG)
        panels.grid(row=1, column=0, sticky="nsew")
        panels.grid_columnconfigure(0, weight=3, uniform="panels")
        panels.grid_columnconfigure(1, weight=2, uniform="panels")
        panels.grid_rowconfigure(0, weight=1)

        camera_panel = ctk.CTkFrame(
            panels, fg_color=SURFACE, corner_radius=9,
            border_width=1, border_color=BORDER
        )
        camera_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        camera_panel.grid_columnconfigure(0, weight=1)
        camera_panel.grid_rowconfigure(1, weight=1)

        camera_heading = ctk.CTkFrame(camera_panel, fg_color=SURFACE)
        camera_heading.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 12))
        ctk.CTkLabel(
            camera_heading, text="Live camera preview", text_color=TEXT,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        self.camera_badge = ctk.CTkLabel(
            camera_heading, text="CAMERA OFF", corner_radius=5,
            fg_color=SURFACE_ALT, text_color=MUTED,
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.camera_badge.pack(side="right", padx=2, pady=2)

        self.video_label = ctk.CTkLabel(
            camera_panel,
            text="Camera preview\n\nSelect Start monitoring to begin.",
            fg_color=VIDEO_BG, corner_radius=5, text_color="#D4DEE8",
            font=ctk.CTkFont(size=15), justify="center"
        )
        self.video_label.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 16))

        controls = ctk.CTkFrame(camera_panel, fg_color=SURFACE)
        controls.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 18))
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_columnconfigure(1, weight=1)
        self.start_btn = ctk.CTkButton(
            controls, text="Start monitoring", command=self.start_monitoring,
            height=43, corner_radius=6, fg_color=ACCENT,
            hover_color=ACCENT_HOVER, text_color=START_TEXT,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.start_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.stop_btn = ctk.CTkButton(
            controls, text="Stop session", command=self.stop_monitoring,
            height=43, corner_radius=6, fg_color=STOP_BG,
            hover_color=STOP_HOVER, text_color=BAD,
            state="disabled", font=ctk.CTkFont(size=14, weight="bold"),
            border_width=1, border_color=STOP_BORDER
        )
        self.stop_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        side = ctk.CTkFrame(
            panels, fg_color=SURFACE, corner_radius=9,
            border_width=1, border_color=BORDER
        )
        side.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        side.grid_columnconfigure(0, weight=1)
        side.grid_columnconfigure(1, weight=1)
        side.grid_rowconfigure(4, weight=1)
        ctk.CTkLabel(
            side, text="Session overview", text_color=TEXT,
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=17, pady=(16, 10))
        self.timer_label = self.metric(
            side, "SESSION TIME", "00:00:00", row=1, column=0,
            columnspan=2, large=True, value_color=ACCENT
        )
        self.status = self.metric(side, "POSTURE", "Waiting", row=2, column=0)
        self.eye_status = self.metric(side, "EYES", "Waiting", row=2, column=1)
        self.score_label = self.metric(
            side, "FOCUS SCORE", "--", row=3, column=0, value_color=ACCENT
        )
        self.alert_label = self.metric(side, "REMINDERS", "0", row=3, column=1)

        guidance_card = ctk.CTkFrame(
            side, fg_color=GUIDANCE_BG, corner_radius=6,
            border_width=1, border_color=GUIDANCE_BORDER
        )
        guidance_card.grid(
            row=4, column=0, columnspan=2, sticky="nsew",
            padx=14, pady=(8, 10)
        )
        ctk.CTkLabel(
            guidance_card, text="GUIDANCE", text_color=ACCENT,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w", padx=12, pady=(10, 4))
        self.guidance = ctk.CTkLabel(
            guidance_card,
            text="Sit comfortably, keep your back supported and take regular breaks.",
            wraplength=330, justify="left", text_color=TEXT,
            font=ctk.CTkFont(size=12)
        )
        self.guidance.pack(anchor="w", padx=12, pady=(0, 10))
        ctk.CTkLabel(
            side, text="Privacy: camera frames are processed locally and are not saved.",
            wraplength=350, text_color=MUTED, font=ctk.CTkFont(size=10)
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=17, pady=(0, 14))

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(1000, self.update_timer)

    def metric(self, parent, title, value, row, column, columnspan=1,
               large=False, value_color=TEXT):
        box = ctk.CTkFrame(
            parent, fg_color=SURFACE_ALT, corner_radius=6,
            border_width=1, border_color=BORDER
        )
        box.grid(
            row=row, column=column, columnspan=columnspan,
            sticky="nsew", padx=5, pady=5
        )
        ctk.CTkLabel(
            box, text=title, text_color=MUTED,
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w", padx=12, pady=(10, 2))
        label = ctk.CTkLabel(
            box, text=value, text_color=value_color, wraplength=250,
            font=ctk.CTkFont(size=26 if large else 15, weight="bold")
        )
        label.pack(anchor="w", padx=12, pady=(0, 10))
        return label

    def change_theme(self, mode):
        if mode not in ("Light", "Dark"):
            return
        ctk.set_appearance_mode(mode.lower())
        self.theme_toggle.set(mode)

    def start_monitoring(self):
        if self.running:
            return
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Camera error", "Could not open webcam. Check camera permission and close other apps using it.")
            self.cap.release()
            self.cap = None
            return
        self.running = True
        self.started_at = time.time()
        self.posture_events = self.eye_alerts = self.frames = self.good_frames = 0
        self.camera_badge.configure(
            text="MONITORING", fg_color=("#DDF2EC", "#164136"),
            text_color=ACCENT
        )
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.worker = threading.Thread(target=self.camera_loop, daemon=True)
        self.worker.start()

    def camera_loop(self):
        while self.running and self.cap:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.05)
                continue
            frame = cv2.flip(frame, 1)
            result = self.monitor.analyze(frame)
            self.frames += 1
            if result["posture"] == "Good":
                self.good_frames += 1
            else:
                self.posture_events += 1
            if result["eyes"] == "Take a break":
                self.eye_alerts += 1

            cv2.putText(frame, "Posture: " + result["posture"], (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 220, 130), 2)
            cv2.putText(frame, "Eyes: " + result["eyes"], (15, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 220, 130), 2)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(rgb)
            self.after(0, self.update_video, img, result)
            time.sleep(0.02)

    def update_video(self, img, result):
        if not self.running:
            return
        w = max(480, self.video_label.winfo_width())
        h = max(300, self.video_label.winfo_height())
        img.thumbnail((w, h))
        photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.video_label.configure(image=photo, text="")
        self.video_label.image = photo
        posture_color = GOOD if result["posture"] == "Good" else WARNING
        eye_color = GOOD if result["eyes"] == "Normal" else WARNING
        self.status.configure(text=result["posture"], text_color=posture_color)
        self.eye_status.configure(text=result["eyes"], text_color=eye_color)
        self.guidance.configure(text=result["message"])
        now = time.time()
        for key, text in (("posture", "Please sit upright and relax your shoulders."), ("eyes", "Look away from the screen and blink naturally.")):
            bad = (key == "posture" and result["posture"] == "Adjust posture") or (key == "eyes" and result["eyes"] == "Take a break")
            if bad and now - self.last_alert.get(key, 0) > 45:
                notify("FocusGuard AI", text)
                self.last_alert[key] = now

    def stop_monitoring(self):
        if not self.running:
            return
        self.running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        elapsed = max(1, int(time.time() - self.started_at)) if self.started_at else 1
        score = calculate_focus_score(self.good_frames, self.frames, self.posture_events, self.eye_alerts)
        self.db.save_session(elapsed, score, self.posture_events, self.eye_alerts)
        self.score_label.configure(text=f"{score}/100")
        self.alert_label.configure(text=str(self.posture_events + self.eye_alerts))
        self.camera_badge.configure(
            text="CAMERA OFF", fg_color=SURFACE_ALT, text_color=MUTED
        )
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.video_label.configure(
            image=None,
            text="Session saved\n\nStart monitoring whenever you're ready.",
            text_color=("#D4DEE8", "#D4DEE8")
        )
        self.video_label.image = None

    def update_timer(self):
        if self.running and self.started_at:
            seconds = int(time.time() - self.started_at)
            self.timer_label.configure(text=f"{seconds//3600:02}:{(seconds%3600)//60:02}:{seconds%60:02}")
        self.after(1000, self.update_timer)

    def analytics(self):
        show_analytics(self, self.db)

    def saved_sessions(self):
        show_saved_sessions(self, self.db)

    def on_close(self):
        if self.running:
            self.stop_monitoring()
        self.destroy()

if __name__ == "__main__":
    app = FocusGuardApp()
    app.mainloop()
