import calendar
import datetime
import tkinter as tk
from tkinter import ttk
from caldav import DAVClient
from PIL import Image, ImageTk
import tkinter.font as tkFont


class CalendarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ===== Fonts =====
        self.APP_FONT = tkFont.nametofont("TkDefaultFont")
        self.APP_FONT.configure(size=12)

        self.APP_FONT_TITLE = tkFont.nametofont("TkDefaultFont")
        self.APP_FONT_TITLE.configure(size=25)

        self.APP_FONT_BOLD = ("TkDefaultFont", 12, "bold")
        self.APP_FONT_TITLE_BOLD = ("TkDefaultFont", 30, "bold")
        self.APP_FONT_SMALL = ("Arial", 8)
        self.APP_FONT_SMALL_BOLD = ("Arial", 8, "bold")

        # ===== Background =====
        self.bg_image = Image.open("pics/backgrounds/Calendar.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)
        self.bg_label.lower()

        # Load background image
        self.original_bg = Image.open("pics/backgrounds/Calendar.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.original_bg)

        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        # Bind resize event
        self.bind("<Configure>", self._resize_bg)

        # ===== Title =====
        self.title_label = tk.Label(
            self,
            text="Calendar",
            font=self.APP_FONT_TITLE_BOLD,
            bg="#ffffff"
        )
        self.title_label.pack(side="top", pady=10)

        # ===== Weather Icon (top left) =====
        weather_image = Image.open("pics/icons/weather.png")

        # Resize the weather image (adjust size as needed, e.g., 40x40 px)
        weather_image = weather_image.resize((40, 40), Image.Resampling.LANCZOS)

        self.weatherImg = ImageTk.PhotoImage(weather_image)
        self.weather_icon = tk.Label(
            self,
            image=self.weatherImg,
            cursor="hand2",
            bg="#ffffff"
        )
        self.weather_icon.place(x=15, y=15)

        # ===== Calendar Frame =====
        self.calendar_frame = tk.Frame(self, bg="#ffffff")

        # Pack with center alignment and margin
        self.calendar_frame.pack(
            fill="none",
            expand=True,
            padx=50,
            pady=80
        )

        self._build_calendar_ui()

    def _build_calendar_ui(self):
        """Builds a simple month view using Python's calendar module."""
        now = datetime.datetime.now()
        year, month = now.year, now.month

        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(year, month)

        # Header
        header = tk.Label(
            self.calendar_frame,
            text=f"{calendar.month_name[month]} {year}",
            font=self.APP_FONT_TITLE_BOLD,
            bg="#ffffff"
        )
        header.grid(row=0, column=0, columnspan=7, pady=10)

        # Weekday labels
        for idx, day in enumerate(calendar.day_abbr):
            lbl = tk.Label(
                self.calendar_frame,
                text=day,
                font=self.APP_FONT_BOLD,
                bg="#ffffff"
            )
            lbl.grid(row=1, column=idx, padx=5, pady=5)

        # Days
        for row_idx, week in enumerate(month_days, start=2):
            for col_idx, day in enumerate(week):
                if day == 0:
                    text = ""  # empty cell
                else:
                    text = str(day)

                lbl = tk.Label(
                    self.calendar_frame,
                    text=text,
                    font=self.APP_FONT,
                    width=4,
                    height=2,
                    relief="ridge",
                    borderwidth=1,
                    bg="#f9f9f9" if text else "#ffffff"
                )
                lbl.grid(row=row_idx, column=col_idx, padx=2, pady=2, sticky="nsew")

        # Make all columns expand equally
        for col in range(7):
            self.calendar_frame.grid_columnconfigure(col, weight=1)

    def _resize_bg(self, event):
        """Resize background image dynamically to match frame size."""
        new_width = event.width
        new_height = event.height

        resized = self.original_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized)

        self.bg_label.config(image=self.bg_photo)
        self.bg_label.image = self.bg_photo
