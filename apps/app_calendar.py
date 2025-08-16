import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import calendar
import datetime

class CalendarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Fonts
        self.APP_FONT = ("TkDefaultFont", 12)
        self.APP_FONT_TITLE_BOLD = ("TkDefaultFont", 30, "bold")
        self.APP_FONT_BOLD = ("TkDefaultFont", 12, "bold")
        self.APP_FONT_SMALL = ("Arial", 8)

        # Background
        self.bg_image = Image.open("pics/backgrounds/Calendar.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)
        self.bind("<Configure>", self.resize_background)

        # Page title (top-center)
        self.APP_FONT_BOLD = ("TkDefaultFont", 12, "bold")
        self.APP_FONT_TITLE_BOLD = ("TkDefaultFont", 30, "bold")
        title = tk.Label(
            self,
            text="Calendar",
            font=self.APP_FONT_TITLE_BOLD,
            bg="#ffffff",
            fg="#000000"
        )
        title.place(relx=0.5, rely=0.02, anchor="n")

        # Weather glyph (top-left)
        weather_image = Image.open("pics/icons/weather.png").resize((50, 50), Image.Resampling.LANCZOS)
        self.weatherImg = ImageTk.PhotoImage(weather_image)
        self.weather_icon = tk.Label(
            self,
            image=self.weatherImg,
            cursor="hand2",
            bg="#ffffff"
        )
        self.weather_icon.place(x=10, y=10)

        # Back button (top-right)
        back_image = Image.open("pics/icons/back.png").resize((50, 50), Image.Resampling.LANCZOS)
        self.backImg = ImageTk.PhotoImage(back_image)
        self.back_button = tk.Button(
            self,
            image=self.backImg,           
            cursor="hand2",
            command=self.controller.create_home_screen,
            borderwidth=0,
            bg="#ffffff",
            activebackground="#ffffff"
        )
        #self.back_button.place(relx=0.95, rely=0.02, anchor="ne")
        self.back_button.place(relx=1.0, x=-10, y=10, anchor="ne")

        # Main container
        self.main_container = tk.Frame(self, bg="#ffffff")
        self.main_container.place(relx=0, rely=0.1, relwidth=1, relheight=0.9)

        # Left panel (events)
        self.left_panel = tk.Frame(self.main_container)
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(10,5), pady=10)

        self.event_listbox_frame = tk.Frame(self.left_panel)
        self.event_listbox_frame.pack(fill="both", expand=True)

        self.event_listbox = tk.Listbox(self.event_listbox_frame, font=self.APP_FONT_SMALL)
        self.event_listbox.pack(side="left", fill="both", expand=True)

        self.event_scrollbar = tk.Scrollbar(self.event_listbox_frame, orient="vertical", command=self.event_listbox.yview)
        self.event_scrollbar.pack(side="right", fill="y")
        self.event_listbox.config(yscrollcommand=self.event_scrollbar.set)

        # Right panel (calendar)
        self.calendar_frame = tk.Frame(self.main_container)
        self.calendar_frame.pack(side="right", fill="both", expand=True, padx=(5,10), pady=10)

        # Current month/year
        today = datetime.date.today()
        self.current_year = today.year
        self.current_month = today.month

        # Build UI
        self.refresh_calendar()

    # ------------------------------
    # Dynamic resizing methods
    # ------------------------------
    def resize_background(self, event):
        self.bg_resized = self.bg_image.resize((event.width, event.height))
        self.bg_photo = ImageTk.PhotoImage(self.bg_resized)
        self.bg_label.config(image=self.bg_photo)

    def resize_title_font(self, event):
        new_size = max(16, event.width // 30)
        self.title_label.config(font=("TkDefaultFont", new_size, "bold"))

    # ------------------------------
    # Calendar methods
    # ------------------------------
    def refresh_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        self._build_calendar_ui()

        # Show today’s events if in current month
        today = datetime.date.today()
        if today.year == self.current_year and today.month == self.current_month:
            self.show_events_for_date(today)

    def _build_calendar_ui(self):
        cal = calendar.Calendar(firstweekday=6)  # Sunday first
        month_days = cal.monthdatescalendar(self.current_year, self.current_month)

        # Weekday headers
        for c, day in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
            lbl = tk.Label(self.calendar_frame, text=day, font=self.APP_FONT_BOLD)
            lbl.grid(row=0, column=c, sticky="nsew", padx=2, pady=2)
            self.calendar_frame.columnconfigure(c, weight=1)

        # Day cells
        for r, week in enumerate(month_days):
            for c, cell_date in enumerate(week):
                lbl_text = str(cell_date.day)
                lbl_bg = "#ffffff"
                if cell_date.month != self.current_month:
                    lbl_fg = "#888888"
                else:
                    lbl_fg = "#000000"
                    if cell_date == datetime.date.today():
                        lbl_bg = "#a0d8f0"

                lbl = tk.Label(self.calendar_frame, text=lbl_text, bg=lbl_bg, fg=lbl_fg,
                               font=self.APP_FONT_SMALL, borderwidth=1, relief="solid")
                lbl.grid(row=r+1, column=c, sticky="nsew", padx=1, pady=1)
                lbl.bind("<Button-1>", lambda e, d=cell_date: self.show_events_for_date(d))
            self.calendar_frame.rowconfigure(r+1, weight=1)

    # ------------------------------
    # Event methods
    # ------------------------------
    def show_events_for_date(self, date):
        events = self.fetch_icloud_events(date)
        if not events:
            events = ["No events"]
        self.event_listbox.delete(0, tk.END)
        for e in events:
            self.event_listbox.insert(tk.END, e)
        if self.event_listbox.size() > 0:
            self.event_listbox.see(0)
            self.event_listbox.selection_clear(0, tk.END)
            self.event_listbox.selection_set(0)

    def fetch_icloud_events(self, date):
        """
        Replace this with real iCloud fetching. For now, dummy events:
        """
        dummy_events = [
            f"Event 1 on {date.strftime('%Y-%m-%d')}",
            f"Event 2 on {date.strftime('%Y-%m-%d')}",
            f"Event 3 on {date.strftime('%Y-%m-%d')}",
        ]
        return dummy_events
