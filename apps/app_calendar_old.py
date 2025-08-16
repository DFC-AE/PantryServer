import calendar
import datetime
import tkinter as tk
from tkinter import ttk
from caldav import DAVClient
from PIL import Image, ImageTk
import tkinter.font as tkFont

#ICLOUD_USERNAME = "your_icloud_email"
#ICLOUD_PASSWORD = "your_app_specific_password"
ICLOUD_USERNAME = "dfc008@latech.edu"
ICLOUD_PASSWORD = "?V@ugl@ge69!"

class CalendarPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Define fonts after Tk root exists
        self.APP_FONT = tkFont.nametofont("TkDefaultFont")
        self.APP_FONT.configure(size=12)

        self.APP_FONT_TITLE = tkFont.nametofont("TkDefaultFont")
        self.APP_FONT_TITLE.configure(size=25)

        self.APP_FONT_BOLD = ("TkDefaultFont", 12, "bold")
        self.APP_FONT_TITLE_BOLD = ("TkDefaultFont", 30, "bold")
        self.APP_FONT_SMALL = ("Arial", 8)
        self.APP_FONT_SMALL_BOLD = ("Arial", 8, "bold")

        # Background image
        self.bg_image = Image.open("pics/backgrounds/Calendar.jpg")
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)

        # Page title
        title = tk.Label(self, text="Calendar", font=self.APP_FONT_BOLD, bg="#ffffff", fg="#000000")
        title.pack(side="top", pady=10)

        # Weather glyph (top left)
        weather_image = Image.open("pics/icons/weather.png")
        self.weatherImg = ImageTk.PhotoImage(weather_image)
        self.weather_icon = tk.Label(self, image=self.weatherImg, cursor="hand2", bg="#ffffff")
        self.weather_icon.place(x=10, y=10)

        # Weather glyph (top left)
        self.weather_icon = tk.Label(self, image=weatherImg, cursor="hand2", font=("Arial", 20), bg="#ffffff")
        self.weather_icon.place(x=10, y=10)

        # Back button (top right)
        #back_btn = tk.Button(self, image=backImg, cursor="hand2", command=lambda: controller.show_frame("HomePage"))
        back_btn = tk.Button(self, text="Back", command=lambda: self.controller.create_home_screen())
        back_btn.place(relx=0.95, y=10, anchor="ne")

        # Split into two panels
        self.left_panel = tk.Frame(self, bg="#f0f0f0")
        self.left_panel.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.right_panel = tk.Frame(self, bg="#ffffff")
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Today's events title
        today_label = tk.Label(self.left_panel, text="Today's Events", font=("Arial", 16, "bold"), bg="#f0f0f0")
        today_label.pack(pady=5)

        # Event list (Treeview)
        self.tree = ttk.Treeview(self.left_panel, columns=("Event", "Time"), show="headings")
        self.tree.heading("Event", text="Event")
        self.tree.heading("Time", text="Time")
        self.tree.pack(fill="both", expand=True)

        # Full month calendar
        self.calendar_widget = tk.Text(self.right_panel, font=("Courier", 12))
        self.calendar_widget.pack(fill="both", expand=True)
        self.show_month_calendar()

        # Load events
        self.load_events()

    def show_month_calendar(self):
        now = datetime.datetime.now()
        month_calendar = calendar.month(now.year, now.month)
        self.calendar_widget.delete(1.0, "end")
        self.calendar_widget.insert("end", month_calendar)

    def load_events(self):
        try:
            client = DAVClient("https://caldav.icloud.com/", username=ICLOUD_USERNAME, password=ICLOUD_PASSWORD)
            principal = client.principal()
            calendars = principal.calendars()

            today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + datetime.timedelta(days=1)

            self.tree.delete(*self.tree.get_children())

            for cal in calendars:
                events = cal.date_search(today, tomorrow)
                for event in events:
                    vcal = event.vobject_instance
                    summary = vcal.vevent.summary.value
                    start_time = vcal.vevent.dtstart.value
                    if isinstance(start_time, datetime.datetime):
                        start_time_str = start_time.strftime("%H:%M")
                    else:
                        start_time_str = "All Day"
                    self.tree.insert("", "end", values=(summary, start_time_str))
        except Exception as e:
            print(f"Error loading events: {e}")

#    def open_calendar_page(self):
#        # Clear the current screen
#        self.clear_screen()

        # Create the CalendarPage
#        calendar_page = CalendarPage(self.root, self)
#        calendar_page.pack(expand=True, fill="both")
