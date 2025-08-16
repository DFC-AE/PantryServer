import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import calendar
import datetime
from caldav import DAVClient

class CalendarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ===== Background =====
        self.original_bg = Image.open("pics/backgrounds/Calendar.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.original_bg)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        # ===== Title =====
        self.title_label = tk.Label(self, text="Calendar", font=("TkDefaultFont", 30, "bold"), bg="#ffffff")
        self.title_label.place(x=self.winfo_width()/2, y=10, anchor="n")

        # ===== Back button =====
        self.original_back_image = Image.open("pics/icons/back.png")
        back_image_resized = self.original_back_image.resize((50, 50), Image.Resampling.LANCZOS)
        self.backImg = ImageTk.PhotoImage(back_image_resized)
        self.back_button = tk.Button(self, image=self.backImg, command=lambda: controller.show_frame("home"),
                                     cursor="hand2", bd=0, highlightthickness=0)
        self.back_button.place(x=self.winfo_width() - 60, y=10)

        # ===== Weather glyph =====
        self.original_weather_image = Image.open("pics/icons/weather.png")
        weather_image_resized = self.original_weather_image.resize((40, 40), Image.Resampling.LANCZOS)
        self.weatherImg = ImageTk.PhotoImage(weather_image_resized)
        self.weather_icon = tk.Label(self, image=self.weatherImg, cursor="hand2", bg="#ffffff")
        self.weather_icon.place(x=10, y=10)

        # ===== Main panels =====
        self.left_panel = tk.Frame(self, bg="#f0f0f0", bd=1, relief="sunken")
        self.right_panel = tk.Frame(self, bg="#ffffff", bd=1, relief="sunken")
        self.left_panel.place(x=10, y=100, width=250, height=400)  # placeholder, will resize
        self.right_panel.place(x=270, y=100, width=500, height=400)  # placeholder, will resize

        # ===== Scrollable today’s events list =====
        self.event_listbox = tk.Listbox(self.left_panel, font=("TkDefaultFont", 12))
        self.event_scrollbar = tk.Scrollbar(self.left_panel, orient="vertical", command=self.event_listbox.yview)
        self.event_listbox.config(yscrollcommand=self.event_scrollbar.set)
        self.event_listbox.pack(side="left", fill="both", expand=True)
        self.event_scrollbar.pack(side="right", fill="y")

        # Sample events for today
        today = datetime.date.today()
        sample_events = [f"Event {i+1} at {i+9}AM" for i in range(5)]
        for e in sample_events:
            self.event_listbox.insert(tk.END, e)

        # ===== Calendar frame inside right panel =====
        self.calendar_frame = tk.Frame(self.right_panel, bg="#ffffff")
        self.calendar_frame.pack(fill="both", expand=True)
        self.current_month = datetime.datetime.now().month
        self.current_year = datetime.datetime.now().year
        self._build_calendar_ui(width=self.right_panel.winfo_width(), height=self.right_panel.winfo_height())

        # ===== Bind resize =====
        self.bind("<Configure>", self._on_resize)

    def _build_calendar_ui(self, width, height):
        # Clear previous widgets
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        # Scale font and cell sizes
        scale_x = width / 500  # base right panel width
        scale_y = height / 400  # base right panel height
        scale = min(scale_x, scale_y)
        scale = max(scale, 1)
        cell_font = ("TkDefaultFont", int(12*scale))
        cell_width = int(8*scale)
        cell_height = int(4*scale)

        # Get current month calendar
        cal = calendar.monthcalendar(self.current_year, self.current_month)

        # Weekday headers
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day in enumerate(days):
            tk.Label(self.calendar_frame, text=day, font=cell_font, width=cell_width, height=1, bg="#cccccc").grid(row=0, column=i)

        # Dates
        for r, week in enumerate(cal):
            for c, day in enumerate(week):
                text = str(day) if day != 0 else ""
                tk.Label(self.calendar_frame, text=text, font=cell_font, width=cell_width, height=cell_height,
                         bg="#ffffff", relief="ridge", borderwidth=1).grid(row=r+1, column=c)

    def _on_resize(self, event):
        new_width = event.width
        new_height = event.height

        # ===== Resize background =====
        resized_bg = self.original_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_bg)
        self.bg_label.config(image=self.bg_photo)
        self.bg_label.image = self.bg_photo

        # ===== Scaling factor =====
        scale_x = new_width / 800
        scale_y = new_height / 600
        scale = min(scale_x, scale_y)
        scale = max(scale, 1)

        # ===== Title =====
        self.title_label.config(font=("TkDefaultFont", int(30*scale), "bold"))
        self.title_label.place(x=new_width/2, y=10*scale, anchor="n")
        title_height = int(50*scale)

        # ===== Back button =====
        back_size = int(50*scale)
        back_image_resized = self.original_back_image.resize((back_size, back_size), Image.Resampling.LANCZOS)
        self.backImg = ImageTk.PhotoImage(back_image_resized)
        self.back_button.config(image=self.backImg)
        padding = int(10*scale)
        self.back_button.place(x=new_width - back_size - padding, y=padding)

        # ===== Weather glyph =====
        weather_size = int(40*scale)
        weather_image_resized = self.original_weather_image.resize((weather_size, weather_size), Image.Resampling.LANCZOS)
        self.weatherImg = ImageTk.PhotoImage(weather_image_resized)
        self.weather_icon.config(image=self.weatherImg)
        self.weather_icon.place(x=padding, y=padding)

        # ===== Panels layout =====
        left_width = int(new_width * 0.3)
        right_width = int(new_width * 0.65)
        panel_height = int(new_height - title_height - 2*padding)
        self.left_panel.place(x=padding, y=title_height + padding, width=left_width, height=panel_height)
        self.right_panel.place(x=left_width + 2*padding, y=title_height + padding, width=right_width, height=panel_height)

        # ===== Calendar =====
        self._build_calendar_ui(width=right_width, height=panel_height)
