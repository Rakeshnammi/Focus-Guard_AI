import customtkinter as ctk

APP_BG = ("#F2F5F9", "#111827")
SURFACE = ("#FFFFFF", "#1E293B")
SURFACE_ALT = ("#F7F9FC", "#263449")
ACCENT = ("#167D6A", "#34D399")
TEXT = ("#182B3A", "#F8FAFC")
MUTED = ("#647789", "#A6B4C4")
BORDER = ("#DCE4EC", "#334155")


def _active_color(color):
    return color[1] if ctk.get_appearance_mode() == "Dark" else color[0]


def show_saved_sessions(parent, db):
    rows = db.get_sessions(limit=None)
    win = ctk.CTkToplevel(parent)
    win.title("FocusGuard AI | Session History")
    win.geometry("940x620")
    win.minsize(760, 440)
    win.configure(fg_color=APP_BG)
    win.grid_columnconfigure(0, weight=1)
    win.grid_rowconfigure(1, weight=1)

    ctk.CTkLabel(
        win, text=f"SESSION HISTORY  |  {len(rows)} saved",
        text_color=TEXT, font=ctk.CTkFont(size=22, weight="bold")
    ).grid(row=0, column=0, padx=20, pady=(18, 12), sticky="w")

    if not rows:
        ctk.CTkLabel(
            win,
            text="No saved sessions yet. Stop a monitoring session to save it here.",
            text_color=MUTED
        ).grid(row=1, column=0, padx=20, pady=20, sticky="nw")
        return

    table = ctk.CTkScrollableFrame(
        win, label_text="Newest sessions first",
        fg_color=SURFACE, label_text_color=MUTED,
        corner_radius=6, border_width=1, border_color=BORDER
    )
    table.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
    columns = (
        ("Date and time", 2),
        ("Duration", 1),
        ("Focus score", 1),
        ("Posture alerts", 1),
        ("Eye alerts", 1),
    )
    for column, (heading, weight) in enumerate(columns):
        table.grid_columnconfigure(column, weight=weight)
        ctk.CTkLabel(
            table, text=heading, text_color=ACCENT,
            font=ctk.CTkFont(size=11, weight="bold"), anchor="w"
        ).grid(row=0, column=column, padx=8, pady=8, sticky="ew")

    for row_index, row in enumerate(rows, start=1):
        created_at, duration, score, posture_events, eye_alerts = row
        values = (
            created_at.replace("T", " "),
            f"{duration // 3600:02}:{(duration % 3600) // 60:02}:{duration % 60:02}",
            f"{score}/100",
            str(posture_events),
            str(eye_alerts),
        )
        for column, value in enumerate(values):
            ctk.CTkLabel(
                table, text=value, text_color=TEXT, anchor="w",
                fg_color=SURFACE_ALT if row_index % 2 == 0 else SURFACE,
                corner_radius=0
            ).grid(row=row_index, column=column, padx=8, pady=6, sticky="ew")


def show_analytics(parent, db):
    rows = db.get_sessions()
    win = ctk.CTkToplevel(parent)
    win.title("FocusGuard AI | Analytics")
    win.geometry("840x620")
    win.minsize(680, 500)
    win.configure(fg_color=APP_BG)
    ctk.CTkLabel(
        win, text="Session analytics", text_color=TEXT,
        font=ctk.CTkFont(size=23, weight="bold")
    ).pack(anchor="w", padx=24, pady=(22, 14))
    if not rows:
        ctk.CTkLabel(
            win,
            text="No completed sessions yet. Start monitoring and stop a session to create your first record.",
            text_color=MUTED
        ).pack(anchor="w", padx=24, pady=20)
        return

    scores = [row[2] for row in reversed(rows)]
    try:
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        surface = _active_color(SURFACE)
        text = _active_color(TEXT)
        muted = _active_color(MUTED)
        accent = _active_color(ACCENT)
        border = _active_color(BORDER)
        fig = Figure(figsize=(7.6, 4.0), dpi=100, facecolor=surface)
        ax = fig.add_subplot(111)
        ax.set_facecolor(surface)
        ax.plot(
            range(1, len(scores) + 1), scores, marker="o",
            color=accent, linewidth=2.5, markersize=6,
            markerfacecolor=accent, markeredgecolor=surface
        )
        ax.set_title("Focus score by session", color=text, pad=14, fontweight="bold")
        ax.set_xlabel("Session (oldest to newest)", color=muted, labelpad=10)
        ax.set_ylabel("Focus score / 100", color=muted, labelpad=10)
        ax.set_ylim(0, 100)
        ax.tick_params(colors=muted)
        ax.grid(True, color=border, alpha=0.8)
        for spine in ax.spines.values():
            spine.set_color(border)
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)
    except Exception as exc:
        ctk.CTkLabel(
            win, text=f"Chart could not be displayed: {exc}", text_color=MUTED
        ).pack(pady=10)

    average_score = round(sum(scores) / len(scores), 1)
    total_minutes = sum(row[1] for row in rows) // 60
    summary = ctk.CTkFrame(win, fg_color=SURFACE, corner_radius=13)
    summary.pack(fill="x", padx=20, pady=(8, 12))
    ctk.CTkLabel(
        summary,
        text=f"{len(scores)} sessions     Average score  {average_score}/100     Study time  {total_minutes} min",
        text_color=TEXT, font=ctk.CTkFont(size=14, weight="bold")
    ).pack(anchor="w", padx=16, pady=13)
    ctk.CTkLabel(
        win, text="Scores are approximate app indicators, not medical or scientific measurements.",
        text_color=MUTED
    ).pack(pady=(0, 14))
