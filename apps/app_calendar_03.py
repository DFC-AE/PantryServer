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

        self.APP_FONT_TITLE_BOLD = ("TkDefaultFont", 30, "bold")
        self.APP_FONT_BOLD = ("TkDefaultFont", 12, "bold")
        self.APP_FONT_SMALL = ("Arial", 8)
        self.APP_FONT_SMALL_BOLD = ("Arial", 8, "bold")

        # ===== Background =====
        self.original_bg = Image.open("pics/backgrounds/Calendar.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.original_bg)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)
        self.bg_label.lower()  # keep behind everything
        self.bind("<Configure>", self._on_resize)

        # ===== Title =====
        self.title_label = tk.Label(
            self,
            text="Calendar",
            font=self.APP_FONT_TITLE_BOLD,
            bg="#ffffff"
        )
        self.title_label.place(relx=0.5, rely=0.05, anchor="n")  # top-center

        # ===== Back Button =====
        back_image = Image.open("pics/icons/back.png").resize((50, 50), Image.Resampling.LANCZOS)
        self.backImg = ImageTk.PhotoImage(back_image)
        self.back_button = tk.Button(
            self,
            image=self.backImg,
            command=lambda: self.controller.show_frame("home"),
            cursor="hand2",
            bd=0,
            highlightthickness=0
        )
        self.back_button.place(relx=0.95, rely=0.05, anchor="ne")  # top-right

        # ===== Weather Icon =====
        weather_image = Image.open("pics/icons/weather.png").resize((40, 40), Image.Resampling.LANCZOS)
        self.weatherImg = ImageTk.PhotoImage(weather_image)
        self.weather_icon = tk.Label(self, image=self.weatherImg, cursor="hand2", bg="#ffffff")
        self.weather_icon.place(relx=0.05, rely=0.05, anchor="nw")  # top-left

        # ===== Calendar Frame =====
        self.calendar_frame = tk.Frame(self, bg="#ffffff")
        self.calendar_frame.place(x=new_width/2, y=title_height + padding*2, anchor="n")
        #self.calendar_frame.place(relx=0.5, rely=0.15, anchor="n")  # start below title
        self._build_calendar_ui()

    def _on_resize(self, event):
        """Resize background and adjust all widgets dynamically."""
        new_width = event.width
        new_height = event.height

        # ===== Resize background =====
        resized_bg = self.original_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_bg)
        self.bg_label.config(image=self.bg_photo)
        self.bg_label.image = self.bg_photo

        # ===== Scaling factor =====
        #scale = max(1, int(new_width / 800))  # base width 800px

        # ===== Scaling factor =====
        scale_x = new_width / 800
        scale_y = new_height / 600
        scale = min(scale_x, scale_y)
        scale = max(scale, 1)

        # ===== Resize & reposition top widgets =====
        # Title font
        #self.title_label.config(font=("TkDefaultFont", 30 * scale, "bold"))
        self.title_label.config(font=("TkDefaultFont", int(30 * scale), "bold"))
        self.title_label.place(relx=0.5, rely=0.05, anchor="n")

        # Back button
        back_size = 50 * scale
        back_image_resized = self.original_back_image.resize((back_size, back_size), Image.Resampling.LANCZOS)
        self.backImg = ImageTk.PhotoImage(back_image_resized)
        self.back_button.config(image=self.backImg)
        padding = 10 * scale
        self.back_button.place(x=event.width - back_size - padding, y=padding)
        self.weather_icon.place(x=padding, y=padding)
        #self.back_button.place(relx=0.95, rely=0.05, anchor="ne")

        # Weather glyph
        weather_size = 40 * scale
        weather_image_resized = self.original_weather_image.resize((weather_size, weather_size), Image.Resampling.LANCZOS)
        self.weatherImg = ImageTk.PhotoImage(weather_image_resized)
        self.weather_icon.config(image=self.weatherImg)
        self.weather_icon.place(relx=0.05, rely=0.05, anchor="nw")

        # ===== Resize & reposition calendar =====
        self.calendar_frame.place(relx=0.5, rely=0.15, anchor="n")
        self._build_calendar_ui(width=new_width, height=new_height)

    def _build_calendar_ui(self, width=None, height=None):
        """Draws the month calendar inside calendar_frame with dynamic scaling."""
        now = datetime.datetime.now()
        year, month = now.year, now.month
        cal = calendar.Calendar()
        month_days = cal.monthdayscalendar(year, month)

        # Clear previous widgets
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Determine scaling factor (based on width)
        scale = 1
        if width:
            scale = max(1, int(width / 800))  # base width 800px

        #scale_x = event.width / 800   # base width
        #scale_y = event.height / 600  # base height
        #scale = min(scale_x, scale_y)
        #scale = max(scale, 1)

        title_font_size = int(20 * scale)
        day_font_size = int(12 * scale)
        cell_width = 4 * scale
        cell_height = 2 * scale

        # Month header
        header = tk.Label(
            self.calendar_frame,
            text=f"{calendar.month_name[month]} {year}",
            font=("TkDefaultFont", title_font_size, "bold"),
            bg="#ffffff"
        )
        header.grid(row=0, column=0, columnspan=7, pady=10*scale)

        # Weekday labels
        for idx, day in enumerate(calendar.day_abbr):
            lbl = tk.Label(
                self.calendar_frame,
                text=day,
                font=("TkDefaultFont", day_font_size, "bold"),
                bg="#ffffff"
            )
            lbl.grid(row=1, column=idx, padx=5*scale, pady=5*scale)

        # Days
        for row_idx, week in enumerate(month_days, start=2):
            for col_idx, day in enumerate(week):
                text = str(day) if day != 0 else ""
                lbl = tk.Label(
                    self.calendar_frame,
                    text=text,
                    font=("TkDefaultFont", day_font_size),
                    width=cell_width,
                    height=cell_height,
                    relief="ridge",
                    borderwidth=1,
                    bg="#f9f9f9" if text else "#ffffff"
                )
                lbl.grid(row=row_idx, column=col_idx, padx=2*scale, pady=2*scale, sticky="nsew")

        # Make all columns expand equally
        for col in range(7):
            self.calendar_frame.grid_columnconfigure(col, weight=1)
