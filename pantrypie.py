# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import simpledialog, messagebox, Button, Label, StringVar, OptionMenu, Tk, Frame, Button, Label
from tkinter.font import Font as font
## For Calendar ##
from datetime import datetime
from tkcalendar import Calendar, DateEntry
import time
from time import strftime
## For Camera ##
import cv2
from PIL import Image, ImageTk
import itertools
from pyzbar.pyzbar import decode
import matplotlib.pyplot as plt
import os
import sys
## For Database ##
import json
import random
import requests
from pynput import keyboard as pk
from io import BytesIO
## For Music Player ##
#import spotipy
#from spotipy.oauth2 import SpotifyOAuth
import base64
import pygame
import vlc
import webbrowser
## MultiThreading ##
import threading

##setup Virtual Keyboard
# Splashscreen Setup
class SplashScreen(tk.Toplevel):
    def __init__(self, parent, gif_path, delay=3500):

        super().__init__(parent)
        self.parent = parent

        # Remove window decorations
        self.overrideredirect(True)

        # Load frames from an animated GIF
        self.frames = []
        try:
            img = Image.open(gif_path)
            for frame in itertools.count():
                try:
                    img.seek(frame)
                    frame_img = ImageTk.PhotoImage(img.copy())
                    self.frames.append(frame_img)
                except EOFError:
                    break
        except Exception:
            # fallback: single image
            self.frames = [ImageTk.PhotoImage(Image.open(gif_path))]

        # Display first frame
        self.label = tk.Label(self, image=self.frames[0], bg='black')
        self.label.pack()

        # Center the splash on screen
        self.update_idletasks()
        w = self.winfo_reqwidth()
        h = self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Start animating
        self._frame_index = 0
        self._animate()

        # Schedule splash to close after `delay` ms
        self.after(delay, self.destroy)

    def _animate(self):
        if not self.winfo_exists(): 
            return
        self._frame_index = (self._frame_index + 1) % len(self.frames)
        self.label.configure(image=self.frames[self._frame_index])
        # call again after 100ms (adjust for smoother / faster playback)
        self.after(100, self._animate)
# ================= On-Screen Keyboard Integration =================
OSK_WIDTH = 800
OSK_HEIGHT = 300
ACCENT_COL = "#C62145"

class OnScreenKeyboard:

    _current = None

    def __init__(self, parent, target_entry):
        # Close an existing keyboard if it’s still open
        if OnScreenKeyboard._current and OnScreenKeyboard._current.window.winfo_exists():
            OnScreenKeyboard._current._on_close()
        OnScreenKeyboard._current = self

        self.parent = parent
        self.target = target_entry
        self.CAPS = False

        # Make sure the parent’s geometry is up to date
        parent.update_idletasks()
        pw = parent.winfo_width()      # e.g. 1024
        ph = parent.winfo_height()     # e.g. 600
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()

        # Bottom half geometry
        ok_w = pw
        ok_h = ph // 2
        ok_x = px
        ok_y = py + ph - ok_h

        self.window = tk.Toplevel(parent)
        self.window.title("On‑Screen Keyboard")
        # size & position
        self.window.geometry(f"{ok_w}x{ok_h}+{ok_x}+{ok_y}")
        self.window.configure(bg="#1a1a1a")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.lift()

        # A container for all buttons
        self.frame = tk.Frame(self.window, bg="#1a1a1a")
        self.frame.pack(expand=True, fill="both")

        self._build_keys()
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_keys(self):
        # rows of keys: digits, QWERTY, ASDF, ZXCV, specials
        rows = [
            ['1','2','3','4','5','6','7','8','9','0'],
            list('qwertyuiop'),
            list('asdfghjkl'),
            ['Caps'] + list('zxcvbnm') + ['Backspace'],
            ['Space','Enter']
        ]

        btn_font = font(size=14)
        max_cols = max(len(r) for r in rows)

        for r, row in enumerate(rows):
            for c, key in enumerate(row):
                btn = tk.Button(
                    self.frame,
                    text=key,
                    font=btn_font,
                    bg="#333", fg="#fff",
                    relief='flat',
                    command=lambda k=key: self._on_key_press(k)
                )
                btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")

        # Make columns expand evenly
        for c in range(max_cols):
            self.frame.grid_columnconfigure(c, weight=1)

    def _on_key_press(self, key):
        if key == 'Backspace':
            self.target.delete("insert-1c")
            return
        if key == 'Caps':
            self.CAPS = not self.CAPS
            return
        if key == 'Space':
            self.target.insert(tk.INSERT, ' ')
            return
        if key == 'Enter':
            self.target.insert(tk.INSERT, '\n')
            self._on_close()
            return

        # letter or digit
        char = key.upper() if (self.CAPS and key.isalpha()) else key
        self.target.insert(tk.INSERT, char)

    def _on_close(self):
        OnScreenKeyboard._current = None
        self.window.destroy()

## Create Root ##
root = tk.Tk()
root.geometry("1024x600")
#root.geometry("1920x1080")
#root.geometry("3180x2160")
#root.title("Expiration Tracker")
root.title("Pantry Server")

## Variables ##
SAVE_FILE = "items.json"

### Import and Resize Button Images ###
## Button Size ##
img_wdt = 75
img_hgt = 75
## Add Image ##
img_add = Image.open("pics/add.png")
img_add = img_add.resize((img_wdt, img_hgt), Image.LANCZOS)
addImg = ImageTk.PhotoImage(img_add)
## Back Image ##
img_back = Image.open("pics/back.png")
img_back = img_back.resize((img_wdt, img_hgt), Image.LANCZOS)
backImg = ImageTk.PhotoImage(img_back)
## Camera Image ##
img_cam = Image.open("pics/cam.jpg")
img_cam = img_cam.resize((img_wdt, img_hgt), Image.LANCZOS)
camImg = ImageTk.PhotoImage(img_cam)
## Card Image ##
img_card = Image.open("pics/card4.png")
img_card = img_card.resize((img_wdt, img_hgt), Image.LANCZOS)
cardImg = ImageTk.PhotoImage(img_card)
## Light Image ##
img_light = Image.open("pics/light.png")
img_light = img_light.resize((img_wdt, img_hgt), Image.LANCZOS)
lightImg = ImageTk.PhotoImage(img_light)
## Home Image ##
img_home = Image.open("pics/home.png")
img_home = img_home.resize((img_wdt, img_hgt), Image.LANCZOS)
homeImg = ImageTk.PhotoImage(img_home)
## Item Image ##
img_item = Image.open("pics/item.png")
img_item = img_item.resize((img_wdt, img_hgt), Image.LANCZOS)
itemImg = ImageTk.PhotoImage(img_item)
## List Image ##
img_list = Image.open("pics/list.png")
img_list = img_list.resize((img_wdt, img_hgt), Image.LANCZOS)
listImg = ImageTk.PhotoImage(img_list)
## Music Image ##
img_music = Image.open("pics/music.png")
img_music = img_music.resize((img_wdt, img_hgt), Image.LANCZOS)
musicImg = ImageTk.PhotoImage(img_music)
## NPR Image ##
img_npr = Image.open("pics/npr.png")
img_npr = img_npr.resize((img_wdt, img_hgt), Image.LANCZOS)
nprImg = ImageTk.PhotoImage(img_npr)
## Save Image ##
img_save = Image.open("pics/save.jpg")
img_save = img_save.resize((img_wdt, img_hgt), Image.LANCZOS)
saveImg = ImageTk.PhotoImage(img_save)
## Scan Image ##
img_scan = Image.open("pics/scan.jpg")
img_scan = img_scan.resize((img_wdt, img_hgt), Image.LANCZOS)
scanImg = ImageTk.PhotoImage(img_scan)
## Settings Image ##
img_set = Image.open("pics/settings.png")
img_set = img_set.resize((img_wdt, img_hgt), Image.LANCZOS)
setImg = ImageTk.PhotoImage(img_set)
## Spotify Image ##
img_spot = Image.open("pics/spot.png")
img_spot = img_spot.resize((img_wdt, img_hgt), Image.LANCZOS)
spotImg = ImageTk.PhotoImage(img_spot)
## View Image ##
img_view = Image.open("pics/view.png")
img_view = img_view.resize((img_wdt, img_hgt), Image.LANCZOS)
viewImg = ImageTk.PhotoImage(img_view)
## Weather Image ##
img_weather = Image.open("pics/weather.png")
img_weather = img_weather.resize((img_wdt, img_hgt), Image.LANCZOS)
weatherImg = ImageTk.PhotoImage(img_weather)
## Weather Background Image ##
img_back_weather = Image.open("pics/weather.jpg")
img_back_weather = img_back_weather.resize((img_wdt, img_hgt), Image.LANCZOS)
back_weatherImg = ImageTk.PhotoImage(img_back_weather)
## Weather Back Button Image ##
img_back_small = Image.open("pics/back.png").resize((50, 50), Image.LANCZOS)
backsmallImg = ImageTk.PhotoImage(img_back_small)

### Import Barcode Image ###
## Scan ##
img_code = cv2.imread("codes/barcode.png")
## Code ##
img_scan1 = Image.open("codes/barcode.png")
img_scan1 = img_scan1.resize((300, 100), Image.Resampling.LANCZOS)
img_scan2 = ImageTk.PhotoImage(img_scan1)

### Keybindings ###
## Quit with Esc ##
root.bind('<Escape>', lambda e: root.quit())
## Restart with Home ##
def restart_program():
        print("Restarting Program...")
        executable = sys.executable
        ## Windows ##
        if os.name == 'nt':
                os.system(f'start {executable} {" ".join(sys.argv)}')
        ## Linux Mac ##
        else:
                os.execv(executable, [executable] + sys.argv)
        sys.exit()
#root.bind('<Prior>', lambda e: restart_program())
root.bind('<Home>', lambda e: restart_program())

######################## ------- Item Model ------- ################################
class Item:
    def __init__(self, name, expiration_date, nutrition_info=None):
        # Store name and parse expiration date
        self.name = name
        self.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")
        self.nutrition_info = nutrition_info or {}

    def to_dict(self):
        return {
            "name": self.name,
            "expiration_date": self.expiration_date.strftime("%Y-%m-%d"),
            "nutrition_info": self.nutrition_info
        }

    @staticmethod
    def from_dict(data):
        return Item(data['name'], data['expiration_date'], data.get('nutrition_info'))

    @staticmethod
    def from_dict(data):
        return Item(
            data['name'],
            data['expiration_date'],
            data.get('nutrition_info', {})  # optional fallback
        )

    def days_until_expired(self):
        # Return number of days remaining (or negative if expired)
        return (self.expiration_date - datetime.now()).days + 1

    def get_color(self):
        # Return color from red to green based on expiration
        days = self.days_until_expired() - 1
        gradient_colors = [
            "#FF0000", "#FF1A00", "#FF3300", "#FF4D00", "#FF6600", "#FF8000",
            "#FF9900", "#FFB200", "#FFCC00", "#FFE500", "#E5FF00", "#CCFF00",
            "#99FF00", "#66FF00", "#33FF00",
        ]
        if days < 0:
            return gradient_colors[0]
        elif days >= len(gradient_colors):
            return gradient_colors[-1]
        else:
            return gradient_colors[days]

def check_dates(days):
    return abs(days)

## Spotify via Requests ##
## Spotify Credentials ##
#client_id = "YOUR_CLIENT_ID"
client_id = "a25567f1dbcb4a17ab52a0732fae30c5"
#client_secret = "YOUR_CLIENT_SECRET"
client_secret = "3ef33e87da0f44d593ee29a00b250b28"

## Get Token ##
auth_str = f"{client_id}:{client_secret}"
b64_auth_str = base64.b64encode(auth_str.encode()).decode()

token_url = "https://accounts.spotify.com/api/token"
headers = {
    "Authorization": f"Basic {b64_auth_str}"
}
data = {
    "grant_type": "client_credentials"
}

resp = requests.post(token_url, headers=headers, data=data)
spotify_token = resp.json()["access_token"]

# ------- Main Application Class -------
class ExpirationApp:
    def __init__(self, root, spotify_token):
        self.root = root
        self.spotify_token = spotify_token
        self.items = []  # List to hold all items
        self.barcode = barcode = None
        self.current_view = 'home'
        self.dark_mode = False  # Track dark mode state
        self.sort_option = StringVar()
        self.sort_option.set("Sort By")
        self.backgroundImg = ImageTk.PhotoImage(Image.open("pics/back.jpg").resize((1024, 600), Image.LANCZOS))
        self.card_backgroundImg = ImageTk.PhotoImage(Image.open("pics/back_pastel.jpg").resize((1024, 600), Image.LANCZOS))
        self.list_backgroundImg = ImageTk.PhotoImage(Image.open("pics/back_toon.jpg").resize((1024, 600), Image.LANCZOS))
        #self.backImg = PhotoImage(file="pics/back.png")
        self.bg_color = "#f0f0f0"
        self.backImg = ImageTk.PhotoImage(Image.open("pics/back.png").resize((50,50), Image.LANCZOS))
        self.load_items()
        self.init_camera()
        self.create_home_screen()
#        self.weather_ui()

    ## Create Background ##
    def set_background(self):
        background = tk.Label(self.root, image=self.backgroundImg)
        background.place(x=0, y=0, relwidth=1, relheight=1)
        background.lower()

    def open_camera_ui(self):
        self.clear_screen()
        CameraApp(self.root, self.backgroundImg, self.backImg, self.create_home_screen)

    def open_weather_ui(self):
        self.clear_screen()
        #WeatherApp(self.root, self.backgroundImg, self.backImg, self.create_home_screen)
        WeatherApp(self.root, self.backgroundImg, backImg, self.create_home_screen)

    def open_music_ui(self):
        self.clear_screen()
        try:
            MusicApp(self.root, self.backgroundImg, self.backImg, self.create_home_screen, self.spotify_token)
        except Exception as e:
            print("Error Launching MusicApp:", e)

    def open_spotify_ui(self):
        self.clear_screen()
        SpotifyApp(self.root, self.backgroundImg, self.backImg, self.create_home_screen, self.spotify_token)

    def play_npr(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("https://npr-ice.streamguys1.com/live.mp3")
            pygame.mixer.music.play()
            print("NPR stream started.")
        except Exception as e:
            print("Error playing NPR:", e)

    def stop_npr(self):
        pygame.mixer.music.stop()
        print("NPR stream stopped.")

    ## Create Home Screen ##
    def create_home_screen(self, item=None):
    #def create_home_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.clear_screen()
        self.set_background()

	    ## Background Greeting ##
        # Clock at the top
        self.clock_label = tk.Label(self.root, font=('calibri', 30, 'bold'), background='orange', foreground='yellow')
        self.clock_label.pack(pady=10)

        self.weather_label = tk.Label(self.root, font=('calibri', 25), bg='orange', fg='yellow')
        self.weather_label.pack(pady=5)

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

#        button_frame = tk.Frame(self.root)
#        button_grame.pack(pady=20)

        def update_clock():
            string = strftime("%A, %B %d %Y %H:%M:%S")
            if hasattr(self,'clock_label') and self.clock_label.winfo_exists():
                self.clock_label.config(text=string)
                self.root.after(1000, update_clock)

        update_clock()

        def update_weather():
            try:
                city = "Shreveport"  # Change to your preferred city
                api_key = "f63847d7129eb9be9c7a464e1e5ef67b"  # Use your OpenWeatherMap API key
#                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
                url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&units=imperial&appid={api_key}" 
                response = requests.get(url)
                data = response.json()

                ## Show Current Weather ##
                current = data['list'][0]
                temp = current['main']['temp']
                condition = current['weather'][0]['description'].capitalize()
                icon_code = current['weather'][0]['icon']
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
                icon_response = requests.get(icon_url)
                icon_img = Image.open(BytesIO(icon_response.content))
                icon_photo = ImageTk.PhotoImage(icon_img)

                self.weather_icon_label.config(image=icon_photo)
                self.weather_icon_label.image = icon_photo  # prevent GC

                self.weather_label.config(
                    text=f"{city}: {temp:.1f}\u00b0F, {condition}"
                )

                # Weekly forecast (every 8 entries = 24 hrs)
#                for i in range(1, 6):
#                    forecast = data['list'][i * 8]  # approx same time each day
#                    day = datetime.fromtimestamp(forecast['dt']).strftime('%a')
#                    temp = forecast['main']['temp']
#                    condition = forecast['weather'][0]['main']
#                    icon_code = forecast['weather'][0]['icon']
#                    icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
#                    icon_img = Image.open(BytesIO(requests.get(icon_url).content))
#                    icon_photo = ImageTk.PhotoImage(icon_img)

#                    self.forecast_labels[i-1]['icon'].config(image=icon_photo)
#                    self.forecast_labels[i-1]['icon'].image = icon_photo
#                    self.forecast_labels[i-1]['text'].config(text=f"{day}\n{temp:.0f}\u00b0F\n{condition}")

            except Exception as e:
                self.weather_label.config(text="Weather: Unable to load")

 #       def build_weather_ui(self):
 #           self.weather_label = tk.Label(self.root, font=("Arial", 14))
 #           self.weather_label.pack()

#            self.weather_icon_label = tk.Label(self.root)
#            self.weather_icon_label.pack()

#            self.forecast_labels = []
#            frame = tk.Frame(self.root)
#            frame.pack()
#        for _ in range(5):
#            day_frame = tk.Frame(frame)
#            day_frame.pack(side="left", padx=5)

#            icon_label = tk.Label(day_frame)
#            icon_label.pack()
#            text_label = tk.Label(day_frame, font=("Arial", 10))
#            text_label.pack()

#            self.forecast_labels.append({"icon": icon_label, "text": text_label})

        update_weather()

        # Enlarged calendar
        self.cal = Calendar(self.root, selectmode='day', date_pattern="yyyy-mm-dd", background="orange", foreground="yellow", font=('calibri', 15, 'bold'), cursor="hand2")
        self.cal.pack(pady=20, ipady=10, ipadx=10)

        # Buttons side by side
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        item_btn = tk.Button(button_frame, cursor="hand2", image=itemImg, width=100, height=100, command=self.create_list_view)
        item_btn.pack(side=tk.RIGHT)
        ToolTip(item_btn, "Click to Open Food Catalog")

        scan_btn = tk.Button(button_frame, cursor="hand2", image=scanImg, width=100, height=100, command=lambda: self.open_camera_ui())
        scan_btn.pack(side=tk.RIGHT)
        ToolTip(scan_btn, "Click to Scan New Barcodes")

        track_btn = tk.Button(button_frame, cursor="hand2", image=viewImg, width=100, height=100, command=lambda: self.create_tracker_ui(item))
        track_btn.pack(side=tk.RIGHT)
        ToolTip(track_btn, "Click to Enter the Expiration Tracker")

        weather_btn = tk.Button(button_frame, cursor="hand2", image=weatherImg, width=100, height=100, command=lambda: self.open_weather_ui())
        #weather_btn = tk.Button(button_frame, image=weatherImg, width=100, height=100, command=lambda: WeatherApp(self.root))
        weather_btn.pack(side=tk.RIGHT)
        ToolTip(weather_btn, "Click to Open Weather Forcast")

        music_btn = tk.Button(button_frame, cursor="hand2", image=musicImg, width=100, height=100, command=lambda: self.open_music_ui())
        music_btn.pack(side=tk.RIGHT)
        ToolTip(music_btn, "Click to Open Radio")

        npr_btn = tk.Button(button_frame, cursor="hand2", image=nprImg, width=100, height=100, command=lambda: self.play_npr())
        npr_btn.pack(side=tk.RIGHT)
        ToolTip(npr_btn, "Click to Open Nation Public Radio")

        spot_btn = tk.Button(button_frame, cursor="hand2", image=spotImg, width=100, height=100, command=lambda: self.open_spotify_ui())
        spot_btn.pack(side=tk.RIGHT)
        ToolTip(spot_btn, "Click to Open Spotify")

        dark_mode_btn = tk.Button(button_frame, cursor="hand2", image=lightImg, width=100, height=100, command=self.toggle_dark_mode)
        dark_mode_btn.pack(side=tk.LEFT)
#        Hovertip(dark_mode_btn, "Click to Toggle Light/Dark Mode", hover_delay=500)
        ToolTip(dark_mode_btn, "Click to Toggle Light/Dark Mode Test")

        set_btn = tk.Button(button_frame, cursor="hand2", image=setImg, width=100, height=100, command=lambda: self.create_tracker_ui(item))
        set_btn.pack(side=tk.LEFT)
        ToolTip(set_btn, "Click to Configure Application")

#    def get_time():
#        string = strftime("%A, %D %B %Y %R")
#        self.clk.config(text=string)
#        self.clk.after(1000, get_time)

    ## Create Tracker Screen ##
    def create_tracker_ui(self, item):
        self.clear_screen()
        self.set_background()

	## Background Greeting ##
        welcome = Label(root,
                        text = " Expiration Tracker:",
                        font=("Comic Sans MS", 33)).pack()

	## Add Item ##
        add_btn = tk.Button(self.root,
			anchor="n",
			cursor="hand2",
			#text="Add Item",
			image=addImg,
			#command=lambda: self.add_item_popup)
			command=self.add_item_popup)
        add_btn.pack(pady=5)

#        Hovertip(add_btn, "Click to Add Item", hover_delay=500)
        ToolTip(add_btn, "Click to Add Item")

	## Open Camera ##
        cam_btn = tk.Button(self.root,
			cursor="hand2",
			image=camImg,
			#command=self.update_camera)
			### Lambda Breaks Button Here IDKY ###
			#command=lambda: self.show_camera)
			command=self.show_camera)
        cam_btn.pack(pady=5)

#        Hovertip(cam_btn, "Click to Open Camera", hover_delay=500)
        ToolTip(cam_btn, "Click to Open Camera")

	## Show List View ##
        list_view_btn = tk.Button(self.root,
				cursor="hand2",
				#text="List View",
				image=listImg,
				#command=lambda: self.create_list_view)
				command=self.create_list_view)
        list_view_btn.pack(pady=5)

#        Hovertip(list_view_btn, "Click to Open Inventory in List View", hover_delay=500)
        ToolTip(list_view_btn, "Click to Open Inventory in List View")

	## Show Card View ##
        card_view_btn = tk.Button(self.root,
				cursor="hand2",
				#text="Card View",
				image=cardImg,
				#command=lambda: self.create_card_view)
				command=self.create_card_view)
        card_view_btn.pack(pady=5)

#        Hovertip(card_view_btn, "Click to Open Inventory in Card View", hover_delay=500)
        ToolTip(card_view_btn, "Click to Open Inventory in Card View")

	## Mode ##
        dark_mode_btn = tk.Button(self.root,
				cursor="hand2",
				#text="Toggle Dark Mode",
				image=lightImg,
				#command=lambda: self.toggle_dark_mode)
				command=self.toggle_dark_mode)
        dark_mode_btn.pack(pady=10)

#        Hovertip(dark_mode_btn, "Click to Toggle Light/Dark Mode", hover_delay=500)
        ToolTip(dark_mode_btn, "Click to Toggle Light/Dark Mode")

	## Show Back ##
        back_btn = tk.Button(self.root,
			anchor="w",
			cursor="hand2",
			image=backImg,
			command=lambda: self.create_home_screen(None))
        back_btn.pack(pady=10)

#        Hovertip(back_btn, "Click to Return to the Previous Screen", hover_delay=500)
        ToolTip(back_btn, "Click to Return to the Previous Screen")

    ## Create Card view ##
    def create_card_view(self):
        self.clear_screen()

        # Set specific background for card view
        bg_label = tk.Label(self.root, image=self.card_backgroundImg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()

        self.current_view = "card"

        sort_menu = OptionMenu(self.root, self.sort_option, "Expiration (Soonest)", "Expiration (Latest)", "Name (A-Z)", "Name (Z-A)", command=self.sort_items)
        sort_menu.pack(pady=10)

        # Setup scrollable canvas
        #canvas = tk.Canvas(self.root, height=450, bg="SystemButtonFace", highlightthickness=0, bd=0)
        canvas = tk.Canvas(self.root, height=450, bg="lightgray", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        #scroll_frame = tk.Frame(canvas, bg="SystemButtonFace")
        scroll_frame = tk.Frame(canvas, bg="lightgray")


        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=self.root["bg"])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        row = col = 0
        for item in self.items:
            color = item.get_color()
            days = item.days_until_expired()
            text = f"{item.name} - Expires in {check_dates(days)} days" if days >= 0 else f"{item.name} - Expired {check_dates(days)} days ago"
            c_btn = tk.Button(
                scroll_frame, text=text, bg=color, fg="black", font=("Arial", 16), wraplength=150,
                width=15, height=6, highlightthickness=0, bd=1,
                command=lambda i=item: self.show_detail_view(i)
            )
            c_btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col == 3:
                col = 0
                row += 1

        card_back_btn = tk.Button(self.root,
                                  cursor="hand2",
                                  image=backImg,
                                  #command=self.create_home_screen)
                                  command=lambda: [self.stop_camera(), self.create_tracker_ui(None)])
        card_back_btn.pack(pady=10)
#        Hovertip(card_back_btn, "Click to Return to the Previous Screen", hover_delay=500)
        ToolTip(card_back_btn, "Click to Return to the Previous Screen")

    ## Create list view ##
    def create_list_view(self):
        self.clear_screen()
        # Set specific background for list view
        bg_label = tk.Label(self.root, image=self.list_backgroundImg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()

        self.current_view = "list"

        sort_menu = OptionMenu(self.root, self.sort_option, "Expiration (Soonest)", "Expiration (Latest)", "Name (A-Z)", "Name (Z-A)", command=self.sort_items)
        sort_menu.pack(pady=5)

        # Scrollable canvas setup
        #canvas = tk.Canvas(self.root, height=450, bg="SystemButtonFace", highlightthickness=0, bd=0)
        canvas = tk.Canvas(self.root, height=450, bg="lightgray", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        #scroll_frame = tk.Frame(canvas, bg="SystemButtonFace")
        scroll_frame = tk.Frame(canvas, bg="lightgray")


        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=self.root["bg"])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for item in self.items:
            frame = tk.Frame(scroll_frame, bg=self.root["bg"])
            frame.pack(fill=tk.X, pady=2)

            color = item.get_color()
            days = item.days_until_expired()
            text = f"{item.name} - Expires in {check_dates(days)} days" if days >= 0 else f"{item.name} - Expired {check_dates(days)} days ago"
            tk.Label(frame, text=text, bg=color, fg="black", font=("Arial", 14)).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Button(frame, text="Delete", command=lambda i=item: self.delete_item(i)).pack(side=tk.RIGHT, padx=5)

        back_btn = tk.Button(self.root,
                             cursor="hand2",
                             image=backImg,
                             #command=self.create_home_screen)
                             command=lambda: self.create_tracker_ui(None))
        back_btn.pack(pady=10)
#        Hovertip(back_btn, "Click to Return to the Previous Screen", hover_delay=500)
        ToolTip(back_btn, "Click to Return to the Previous Screen")

    def refresh_views(self):
        if self.current_view == "card":
            self.create_card_view()
        elif self.current_view == "list":
            self.create_list_view()

    def show_detail_view(self, item):
        self.current_item = item
        self.clear_screen()
        self.set_background()
        days = item.days_until_expired()

        # Show item details
        detail_text = (
            f"Item: {item.name}\n"
            f"Expiration: {item.expiration_date.strftime('%Y-%m-%d')}\n"
            f"Days Left: {check_dates(days) if days > 0 else 0}"
        )

        # Show nutrition facts on detail screen
        if item.nutrition_info:
            nutrition_frame = tk.Frame(self.root)
            nutrition_frame.place(x=30, y=150)  # Adjust position as needed

            tk.Label(nutrition_frame, text="Nutrition Facts:", font=("Arial", 18, "underline"), anchor="w", justify="left").pack(anchor="w")

            for key, value in item.nutrition_info.items():
                fact = f"{key}: {value}"
                tk.Label(nutrition_frame, text=fact, font=("Arial", 14), anchor="w", justify="left").pack(anchor="w")


        label = tk.Label(self.root, text=detail_text, font=("Arial", 20), justify="left")
        label.pack(pady=30)

        # Scanner and barcode buttons (only shown on item click)
        scanner_btn = tk.Button(self.root,
				cursor="hand2",
				#text="Open Scanner",
				image=camImg,
				#command=lambda: self.show_camera)
				command=self.show_camera)
				#command=lambda: self.detect_barcode_from_camera())
        scanner_btn.pack(pady=5)

#        Hovertip(scanner_btn, "Click to Open Barcode Scanner", hover_delay=500)
        ToolTip(scanner_btn, "Click to Open Barcode Scanner")

        barcode_btn = tk.Button(self.root,
				cursor="hand2",
				#text="Detect Barcode",
				image=scanImg,
				#command=lambda: self.detect_barcode("codes/barcode.png"))
				command=lambda: self.detect_barcode("codes/barcode.png"))
				#command=lambda: self.detect_barcode_from_camera())
        barcode_btn.pack(pady=5)

#        Hovertip(barcode_btn, "Click to Display Scanned Barcode", hover_delay=500)
        ToolTip(barcode_btn, "Click to Display Scanned Barcode")

              # Barcode Entry (auto‑pop OSK on focus)
        label_code = tk.Label(self.root, text="Enter Barcode Number:", font=("Arial", 15), justify="center")
        label_code.pack(pady=5)

        self.barcode_entry = tk.Entry(self.root)
        self.barcode_entry.pack(pady=5)
        self.barcode_entry.bind(
            "<Button-1>",
            lambda e: OnScreenKeyboard(self.root, self.barcode_entry)
        )

#        manual_btn = tk.Button(self.root, text="Enter Barcode", command=self.barcode_entry)
#        manual_btn.pack(pady=10)
#        Hovertip(manual_btn, "Click to Enter Barcode Manually", hover_delay=500)

        # Back to card view
        back_btn = tk.Button(self.root,
			cursor="hand2",
			#text="Back",
			image=cardImg,
			#command=lambda: self.create_card_view)
			command=lambda: [self.stop_camera(), self.create_card_view])
        back_btn.pack(pady=10)
        ToolTip(back_btn, "Click to Return to Card View")

    def barcode_entry(self):
        barcode = simpledialog.askstring("Barcode Entry", "Enter barcode number:")
        if not barcode:
            return
        nutrition_info = self.fetch_open_food_facts(barcode)
        if nutrition_info:
            product_name = nutrition_info.get("Product Name", "")
            if product_name and product_name != "Unknown":
                # Update the item name and nutrition info
                self.current_item.name = product_name
                self.current_item.nutrition_info = nutrition_info
                self.save_items()
                self.show_detail_view(self.current_item)

    def detect_barcode_from_camera(self):
        if hasattr(self, 'cpt') and self.cpt.isOpened():
            self.cpt.release()

        self.cpt = cv2.VideoCapture(0)

        if not self.cpt.isOpened():
            print("Cannot open camera")
            return

        self.update_frame()

    def update_frame(self):
        if not hasattr(self, 'cpt') or not self.cpt.isOpened():
           return

        ret, frame = self.cpt.read()
        if not ret:
            print("Failed to Grab Frame")
            self.cpt.release()
            return

        barcodes = decode(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        for barcode in barcodes:
            data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            print(f"Detected Barcode: {barcode_type} - {data}")

            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, data, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert to ImageTk
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img_pil)

	## Only Update if Camera Label Still Exists ##
        if hasattr(self, 'camera_label') and self.camera_label.winfo_exists():
            self.camera_label.imgtk = imgtk  # prevent garbage collection
            self.camera_label.config(image=imgtk)

        # Schedule the next frame
        self.root.after(10, self.update_frame)

    def fetch_open_food_facts(self, barcode, item=None):
        import requests

        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        print(f"Fetching barcode: {barcode}")  # Debug

        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            if data.get('status') == 1:
                product = data.get('product', {})
                nutriments = product.get('nutriments', {})
                nutrition_info = {
                    "Product Name": product.get('product_name', 'Unknown'),
                    "Calories (kcal)": nutriments.get('energy-kcal_100g', 'N/A'),
                    "Fat (g)": nutriments.get('fat_100g', 'N/A'),
                    "Saturated Fat (g)": nutriments.get('saturated-fat_100g', 'N/A'),
                    "Carbohydrates (g)": nutriments.get('carbohydrates_100g', 'N/A'),
                    "Sugars (g)": nutriments.get('sugars_100g', 'N/A'),
                    "Fiber (g)": nutriments.get('fiber_100g', 'N/A'),
                    "Proteins (g)": nutriments.get('proteins_100g', 'N/A'),
                    "Salt (g)": nutriments.get('salt_100g', 'N/A'),
                    "Sodium (g)": nutriments.get('sodium_100g', 'N/A'),
                    "Serving Size": product.get('serving_size', 'N/A'),
                }

                print("Product found:", nutrition_info["Product Name"])  # Debug

                self.show_nutrition_info(nutrition_info)

                product_name = nutrition_info["Product Name"]

                if hasattr(self, 'name_entry') and self.name_entry.winfo_exists():
                    if product_name and product_name != 'Unknown':
                        self.name_entry.delete(0, tk.END)
                        self.name_entry.insert(0, product_name)

                elif item:
                    if product_name and product_name != 'Unknown':
                        item.name = product_name
                        self.save_items()
                        self.refresh_views()
                return nutrition_info
            else:
                messagebox.showerror("Error", "Product not found in Open Food Facts.")
                return {}
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")
        return nutrition_info

    def show_nutrition_info(self, nutrition_info):
        # Show nutrition information in a popup window
        info_window = tk.Toplevel(self.root)
        info_window.title("Nutrition Information")

        for key, value in nutrition_info.items():
            label = tk.Label(info_window, text=f"{key}: {value}", font=("Arial", 14), anchor="w")
            label.pack(fill=tk.X, padx=10, pady=2)

        close_btn = tk.Button(info_window, text="Close", command=info_window.destroy)
        close_btn.pack(pady=10)

    def sort_items(self, sort_type):
        if sort_type == "Expiration (Soonest)":
            self.items.sort(key=lambda x: x.expiration_date)
        elif sort_type == "Expiration (Latest)":
            self.items.sort(key=lambda x: x.expiration_date, reverse=True)
        elif sort_type == "Name (A-Z)":
            self.items.sort(key=lambda x: x.name.lower())
        elif sort_type == "Name (Z-A)":
            self.items.sort(key=lambda x: x.name.lower(), reverse=True)

        # Refresh the correct view
        if self.current_view == "card":
            self.create_card_view()
        else:
            self.create_list_view()

    def edit_item(self, item):
        # Prompt user to edit name and date
        new_name = simpledialog.askstring("Edit Name", "Enter new name:", initialvalue=item.name)
        new_date = simpledialog.askstring("Edit Date", "Enter new expiration date (YYYY-MM-DD):", initialvalue=item.expiration_date.strftime("%Y-%m-%d"))

        if new_name:
            item.name = new_name
        try:
            if new_date:
                item.expiration_date = datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format.")

        self.refresh_views()

    ## Loads items from file
    def load_items(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                self.items = [Item.from_dict(d) for d in data]

    ## Saves items to file ##
    def save_items(self):
        with open(SAVE_FILE, 'w') as f:
            json.dump([item.to_dict() for item in self.items], f)

    def delete_item(self, item):
        if messagebox.askyesno("Delete", f"Delete {item.name}?"):
            self.items.remove(item)
            self.save_items()
            self.create_list_view()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#2E2E2E" if self.dark_mode else "white"
        fg = "white" if self.dark_mode else "black"
        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

    def add_item_popup(self):
        self.clear_screen()
        self.set_background()

        tk.Label(self.root, text="Add New Item", font=("Comic Sans MS", 30)).pack(pady=10)

        tk.Label(self.root, text="Enter Item Name:", font=("Arial", 15)).pack(pady=5)

        # Item Name Entry (auto‑pop OSK on focus)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)
        # bind focus‑in to launch OSK
        self.name_entry.bind(
            "<Button-1>",
            lambda e: OnScreenKeyboard(self.root, self.name_entry)
        )

        # — Expiration date picker (unchanged) —
        tk.Label(self.root, text="Select Expiration Date:", font=("Arial", 15), justify="center").pack()
        self.date_picker = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.date_picker.pack(pady=5)

        # Barcode Entry (auto‑pop OSK on focus)
        label_code = tk.Label(self.root, text="Enter Barcode Number:", font=("Arial", 15), justify="center")
        label_code.pack(pady=5)

        self.barcode_entry = tk.Entry(self.root)
        self.barcode_entry.pack(pady=5)
        self.barcode_entry.bind(
            "<Button-1>",
            lambda e: OnScreenKeyboard(self.root, self.barcode_entry)
        )

        # Allow barcode to pre-fill name
        #barcode_btn = tk.Button(self.root, text="Enter Barcode to Autofill Name", command=self.barcode_entry())
        #barcode_btn = tk.Button(self.root, text="Enter Barcode to Autofill Name", command=self.barcode_entry)
        #barcode_btn.pack(pady=10)

        scan_btn = tk.Button(self.root,
		#text="Scan",
		cursor="hand2",
		image=scanImg,
		#command=lambda: self.save_new_item).pack(pady=5)
		#command=lambda: self.detect_barcode("codes/barcode.png"))
		#command=lambda: self.detect_barcode_from_camera())
		command=lambda: self.show_camera())

        scan_btn.pack(pady=5)
#        Hovertip(scan_btn, "Click to Show Scanned Barcode", hover_delay=500)
        ToolTip(scan_btn, "Click to Show Scanned Barcode")

        save_btn = tk.Button(self.root,
		#text="Save",
		cursor="hand2",
		image=saveImg,
		#command=lambda: self.save_new_item).pack(pady=5)
		command=self.save_new_item)
        save_btn.pack(pady=5)
#        Hovertip(save_btn, "Click to Save Data", hover_delay=500)
        ToolTip(save_btn, "Click to Save Data")

        mode_btn = tk.Button(self.root,
		#text="Save",
		cursor="hand2",
		image=lightImg,
		#command=lambda: self.save_new_item).pack(pady=5)
		command=self.toggle_dark_mode)
        mode_btn.pack(pady=5)
#        Hovertip(mode_btn, "Click to Toggle Between Light/Dark Mode", hover_delay=500)
        ToolTip(mode_btn, "Click to Toggle Light/Dark Mode")

        back_btn = tk.Button(self.root,
		#text="Back",
		cursor="hand2",
		image=backImg,
		#command=self.create_tracker_ui(None)).pack(pady=5)
		#command=lambda: self.create_tracker_ui(None))
		command=lambda: [self.stop_camera(), self.create_tracker_ui(None)])
        back_btn.pack(pady=5)
#        Hovertip(back_btn, "Click to Return to the Previous Screen", hover_delay=500)
        ToolTip(back_btn, "Click to Return to the Previous Screen")

	## Create Side View of Camera ##
#        self.camera_label = tk.Label(self.root)
#        self.camera_label.pack(pady=10)
#        self.camera_label.pack(pady=10, side="right")
#        self.camera_label.grid(row=0, column=0, columnspan=2, pady=10)

    ## Saves item to list ##
    def save_new_item(self):
        name = self.name_entry.get()
        date = self.date_picker.get()
        barcode = self.barcode_entry.get() if hasattr(self, 'barcode_entry') else ""

        nutrition_info = {}
        product_name = None

        # Step 1: Fetch nutrition and product name if barcode exists
        if barcode:
            fetched_info = self.fetch_open_food_facts(barcode)
            if fetched_info:
                nutrition_info = fetched_info
                product_name = fetched_info.get("Product Name", "")
                if product_name and product_name != "Unknown":
                    name = product_name  #Force overwrite with product name
                    self.name_entry.delete(0, tk.END)
                    self.name_entry.insert(0, name)

        # Step 2: Validate name
        if not name:
            messagebox.showerror("Error", "Item name required")
            return

        # Step 3: Create and save item
        try:
            item = Item(name, date, nutrition_info)
            self.items.append(item)
            self.save_items()
            self.refresh_views()
        except Exception as e:
            messagebox.showerror("Error", f"Could not save item: {e}")

    def clear_screen(self):
        try:
          if hasattr(self, "camera_loop_id"):
            self.root.after_cancel(self.camera_loop_id)
            del self.camera_loop_id
        except Exception as e:
            print("Failed to Cancel Camera Loop:", e)
#        except AttributeError:
#            pass

        for widget in self.root.winfo_children():
            widget.destroy()

    def init_camera(self):
	## Ensure Camera Is Not Currently Open ##
        if hasattr(self, 'cpt') and self.cpt.isOpened():
            self.cpt.release()

	## Open Camera and Store in self.cap ##
        self.cpt = cv2.VideoCapture(0)
        self.cpt.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not self.cpt.isOpened():
           print("Cannot Open Camera")
           return

	## Show Camera Feed ##
        #self.camera_label = tk.Label(self.root)

    def show_camera(self):
        self.clear_screen()
        self.set_background()
        self.init_camera()

        if hasattr(self, 'cpt') and self.cpt.isOpened():
               self.cpt.release()

        ## Create of Reuse Camera Label ##
#        if not hasattr(self, "camera_label") or not self.camera_label.winfo_exists():
#               self.camera_label = tk.Label(self.root)
        self.camera_label = tk.Label(self.root)
        self.camera_label.pack(pady=20, side="top")
        self.update_camera()

        back_btn = tk.Button(self.root,
                             image=backImg,
        		     command=lambda: [self.stop_camera(), self.create_tracker_ui(None)])
                             #command=lambda: self.create_tracker_ui(None))
        back_btn.pack(pady=10, side="left")
#        Hovertip(back_btn, "Click to Return to the Previous Screen", hover_delay=500)
        ToolTip(back_btn, "Click to Return to the Previous Screen")

        scan_btn = tk.Button(self.root,
                             image=scanImg,
                             command=lambda: self.detect_barcode_from_camera())
        scan_btn.pack(pady=10, side="right")
        ToolTip(scan_btn, "Click to Scan Barcode")

        #self.detect_barcode_from_camera()

    def update_camera(self):
      if self.cpt.isOpened():
         if not hasattr(self, "camera_label") or not self.camera_label.winfo_exists():
            return

#      if not self.camera_label.winfo_exists():
#        return

      if hasattr(self, 'cpt') and self.cpt.isOpened():
        ret, frame = self.cpt.read()
        if ret:
            decoded_barcodes = decode(frame)

            if decoded_barcodes:
               for barcode in decoded_barcodes:
                   (x, y, w, h) = barcode.rect
                   cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                   barcode_data = barcode.data.decode("utf-8")
                   barcode_type = barcode.type

                   text = f'{barcode_type}: {barcode_data}'
                   cv2.putText(frame, text, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                   if getattr(self, "last_barcode", None) != barcode_data:
                        print(f"New Barcode Detected: {barcode_data}")
                        self.last_barcode = barcode_data

                   print(f"Scanned: {barcode_data}")

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.config(image=imgtk)
      self.camera_loop_id = self.root.after(10, self.update_camera)

    def stop_camera(self):
        if hasattr(self, 'cpt') and self.cpt.isOpened():
            self.cpt.release()
        if hasattr(self, 'camera_loop_id'):
            self.root.after_cancel(self.camera_loop_id)
        if hasattr(self, 'camera_label'):
            self.camera_label.destroy()

    def stop_camera_loop(self):
        if hasattr(self, "camera_loop_id"):
               self.root.after_cancel(self.camera_loop_id)
        if self.cpt.isOpened():
               self.cpt.release()

    def detect_barcode(self, image_path):
        if not os.path.exists(image_path):
                print("Barcode Image Not Found at:", image_path)
                return

        image = cv2.imread(image_path)
        if image is None:
                print("Failed to Load Image.")
                return

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)

        if not barcodes:
            print("No Barcode Found in Image.")
            return

        for barcode in barcodes:
            data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            print(f"Detected Barcode: {barcode_type} - {data}")

        (x, y, w, h) = barcode.rect
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imshow(rgb)
        plt.axis('off')
        plt.show()

#        self.detect_barcode_from_camera

class ToolTip:
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.id = None

        self.widget.bind("<Enter>", self.schedule)
        self.widget.bind("<Leave>", self.unschedule)
        self.widget.bind("<Motion>", self.move)

    def schedule(self, event=None):
        self.unschedule()
        self.id = self.widget.after(self.delay, self.show_tip)

    def unschedule(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        self.hide_tip()

    def move(self, event):
        if self.tip_window:
            x, y = event.x_root + 20, event.y_root + 10
            self.tip_window.geometry(f"+{x}+{y}")

    def show_tip(self):
        if self.tip_window or not self.text:
            return
        x, y = self.widget.winfo_pointerxy()
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x+20}+{y+10}")
        label = tk.Label(tw, text=self.text, background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", 10, "normal"))
        label.pack(ipadx=1)

    def hide_tip(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

def get_weather(city="Shreveport"):
    api_key = "f63847d7129eb9be9c7a464e1e5ef67b" # Replace with your real API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid={api_key}"

    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            temp = data["main"]["temp"]
            condition = data["weather"][0]["description"].capitalize()
            return f"{city}: {temp}\u00b0F, {condition}"
        else:
            return "Weather not found"
    except Exception as e:
        return f"Error: {e}"

weather_label = tk.Label(root, text="Loading weather...", font=("Arial", 14))
weather_label.pack(pady=20)

def update_weather_old():
    weather = get_weather("Shreveport")  # Change city as needed
#    if not hasattr(self, 'weather_label') or not self.weather_label.winfo_exists():
#       return
    weather_label.config(text=weather)
    root.after(600000, update_weather_old)  # Update every 10 minutes

update_weather_old()

class WeatherApp:
    def __init__(self, root, backgroundImg, backImg, back_callback=None):
    #def __init__(self, root, backImg, back_callback=None):
        self.root = root
        self.root.title("Weather Forecast")
        self.backgroundImg = backgroundImg
        self.backImg = backsmallImg
        #self.backImg = ImageTK.PhotoImage(Image.open("pics/back.png"))
        self.back_callback = back_callback

	## Frame For Weather App Content ##
        self.frame = tk.Frame(self.root)
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.weather_ui()

	## Background Image ##
        #self.backgroundImg = backgroundImg
        #back_weatherImg = tk.PhotoImage(file="pics/weather.jpg")
        pil_weather = Image.open("pics/weather.jpg").resize(
            #(self.root.winfo_screenwidth(), self.root.winfo_screenheight())
            (self.frame.winfo_screenwidth(), self.frame.winfo_screenheight())
        )
        self.backgroundImg = ImageTk.PhotoImage(pil_weather)
#        self.backgroundImg = back_weatherImg
        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.image = self.backgroundImg

	## Back Button Image ##
#        self.backImg = backImg
        self.backImg = ImageTk.PhotoImage(Image.open("pics/back.png"))
        self.back_callback = back_callback
#        self.clear_screen()
#        self.root.geometry("500x400")

        self.city = "Shreveport"
        self.api_key = "f63847d7129eb9be9c7a464e1e5ef67b"  # Your OpenWeatherMap API key

        self.weather_ui()
        #self.update_weather()

    def clear_screen(self):
        #for widget in self.root.winfo_children():
        for widget in self.frame.winfo_children():
            widget.destroy()

    def set_background(self):
      try:
        if hasattr(self, "bg_label"):
           self.bg_label.destroy()
#        if self.backgroundImg:
        #self.bg_label = tk.Label(self.root, image=self.backgroundImg)
        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()
        self.bg_label = bg_label
#        try:
#            self.background_label = tk.Label(self.root, image=backgroundImg)
#            self.background_label.place(relwidth=1, relheight=1)
#        except Exception as e:
#        else:
#           print("No Background Image Set.")
      except Exception as e:
        print("Error setting background:", e)

    def weather_ui(self):
        self.clear_screen()
#        self.set_background()

        ## Set Background Image and Place in the Background ##
        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()
        self.bg_label.image = self.backgroundImg

        ## Main Transparent Content Frame for Layout ##
        content_frame = tk.Frame(self.frame, bg="", padx=10, pady=10)
#        content_frame.place(relx=0.5, rely=0.5, anchor="center")
#        content_frame.pack(fill="both", expand=True)
        content_frame.pack(expand=True)

	## Current Weather Content Frame ##
#        content_frame = tk.Frame(self.root, bg="white", padx=10, pady=10)
#        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        ## Current Weather Label ##
        #self.weather_label = tk.Label(self.root, font=("Arial", 16))
        #self.weather_label = tk.Label(content_frame, font=("Arial", 16), bg="white")
        self.weather_label = tk.Label(content_frame, font=("Arial", 16))
        self.weather_label.pack(pady=10)

        ## Weather Icon ##
        #self.weather_icon_label = tk.Label(self.root)
        #self.weather_icon_label = tk.Label(content_frame, bg="white")
        self.weather_icon_label = tk.Label(content_frame)
        self.weather_icon_label.pack()

        ## Forecast Frame ##
        #forecast_frame = tk.Frame(self.root)
        #forecast_frame = tk.Frame(content_frame, bg="white")
        forecast_frame = tk.Frame(content_frame)
        forecast_frame.pack(pady=10)

        self.forecast_labels = []
        for _ in range(5):
            day_frame = tk.Frame(forecast_frame, borderwidth=1, relief="solid", padx=5, pady=5)
            day_frame.pack(side="left", padx=5)

            #icon_label = tk.Label(day_frame, bg="white")
            icon_label = tk.Label(day_frame)
            icon_label.pack()

            #text_label = tk.Label(day_frame, font=("Arial", 10), bg="white")
            text_label = tk.Label(day_frame, font=("Arial", 10))
            text_label.pack()

            self.forecast_labels.append({"icon": icon_label, "text": text_label})

        ## Back Button ##
        #back_btn = tk.Button(self.root, image="backImg", command=self.create_home_screen)
        #back_btn = tk.Button(self.root, image=self.backImg, command=self.back_callback)
        #back_btn.pack(pady=10)
#        if callable(self.back_callback):
        self.back_btn = tk.Button(self.frame,
                              cursor="hand2",
                              #image=self.backImg,
                              image=backsmallImg,
                                  #command=self.back_callback)
                                  #command=self.back_callback if callable(self.back_callback) else self.root.destroy)
                              command=self.back_callback)
                                  #command=lambda: self.create_home_screen(None))
#        else:
#            self.back_btn = tk.Button(self.root,
#                                  cursor="hand2",
#                                  image=self.backImg,
                                  #command=self.back_callback)
#                                  command=self.root.destroy)
                                  #command=lambda: self.create_home_screen(None))
        #self.back_btn.pack(pady=10)
        self.back_btn.place(relx=0.5, rely=0.95, anchor="s")
        #self.back_btn.place(x=10, y=10, anchor="s")
        self.back_btn.image = self.backImg
        ToolTip(self.back_btn, "Click to Return to the Previous Screen")

        self.update_weather()

    def update_weather(self):
        try:
            if not hasattr(self, 'city'):
                  self.city = "Shreveport"
            if not hasattr(self, 'api_key'):
                  self.api_key = "f63847d7129eb9be9c7a464e1e5ef67b"

            url = f"http://api.openweathermap.org/data/2.5/forecast?q={self.city}&appid={self.api_key}&units=imperial"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if "list" not in data or len(data["list"]) < 6:
               raise ValueError("Incomplete Forecast Data")

            # Current weather
            current = data['list'][0]
            temp = current['main']['temp']
            condition = current['weather'][0]['description'].capitalize()
            icon_code = current['weather'][0]['icon']
            icon_img = self.get_icon(icon_code)

            if not hasattr(self, 'weather_label') or not self.weather_label.winfo_exists():
               return

            self.weather_icon_label.config(image=icon_img)
            self.weather_icon_label.image = icon_img
            self.weather_label.config(text=f"{self.city}: {temp:.1f}\u00b0F, {condition}")

            # 5-day forecast
            for i in range(1, 6):
                index = i * 8
                if index >= len(data['list']):
                   print(f"Skipping Forecast Index {index} (out of range)")
                   continue

                #forecast = data['list'][i * 8]  # 24 hours apart
                forecast = data['list'][index]  # 24 hours apart
                day = datetime.fromtimestamp(forecast['dt']).strftime('%a')
                temp = forecast['main']['temp']
                condition = forecast['weather'][0]['main']
                icon_code = forecast['weather'][0]['icon']
                icon_img = self.get_icon(icon_code)

                self.forecast_labels[i - 1]['icon'].config(image=icon_img)
                self.forecast_labels[i - 1]['icon'].image = icon_img
                self.forecast_labels[i - 1]['text'].config(
                    text=f"{day}\n{temp:.0f}\u00b0F\n{condition}"
                )

        except Exception as e:
            import traceback
            print("Error fetching weather:", e)
            if hasattr(self, "weather_label"):
                 self.weather_label.config(text="Weather: Unable to load")

    def get_icon(self, code):
        try:
            url = f"http://openweathermap.org/img/wn/{code}@2x.png"
            response = requests.get(url)
            img_data = Image.open(BytesIO(response.content))
            return ImageTk.PhotoImage(img_data)
        except Exception as e:
            print("Icon load failed:", e)
            return None

class CameraApp:
    def __init__(self, root, backgroundImg, backImg, back_callback=None):
        self.root = root
        self.backgroundImg = backgroundImg
        self.backImg = backImg
        self.back_callback = back_callback
        self.frame = tk.Frame(self.root)
        self.frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
           print("Failed to Open Camera")
        else:
           print("Camera Opened Successfully")

        self.camera_ui()
        self.update_frame()

    def camera_ui(self):
        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.video_label = tk.Label(self.frame, bg="black")
        self.video_label.place(relx=0.5, rely=0.4, anchor="center")

        self.back_btn = tk.Button(self.frame, image=self.backImg, command=self.back_callback)
        self.back_btn.place(relx=0.5, rely=0.95, anchor="s")

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_label.configure(image=imgtk)
                self.video_label.image = imgtk
        self.frame.after(10, self.update_frame)

## Spotipy ##
#sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#    client_id="YOUR_CLIENT_ID",
#    client_secret="YOUR_CLIENT_SECRET",
#    redirect_uri="http://localhost:8888/callback",
#    scope="user-read-playback-state,user-modify-playback-state,user-read-currently-playing"
#))

#current = sp.current_playback()
#if current:
#    print("Currently Playing:", current['item']['name'])
#else:
#    print("Nothing is playing.")

#play_btn = tk.Button(self.frame, text="Play", command=lambda: sp.start_playback())
#pause_btn = tk.Button(self.frame, text="Pause", command=lambda: sp.pause_playback())
#next_btn = tk.Button(self.frame, text="Next", command=lambda: sp.next_track())

class SpotifyApp:
    def __init__(self, root, backgroundImg, backImg, back_callback, token):
        self.root = root
        self.backgroundImg = backgroundImg
        self.backImg = backImg
        self.back_callback = back_callback
        self.token = token

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        self.create_ui()

    def create_ui(self):
        # Back button
        tk.Button(self.frame, image=self.backImg, command=self.back_callback).place(relx=0.05, rely=0.9)

        # Spotify info
        self.track_label = tk.Label(self.frame, text="Loading...", font=("Arial", 16), bg="white")
        self.track_label.pack(pady=20)

        # Album art
        self.album_art_label = tk.Label(self.frame, bg="white")
        self.album_art_label.pack(pady=10)

        # Control buttons
        controls = tk.Frame(self.frame, bg="white")
        controls.pack(pady=20)

        tk.Button(controls, text="Play", font=("Arial", 14), command=self.play).pack(side=tk.LEFT, padx=10)
        tk.Button(controls, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=10)
        tk.Button(controls, text="Next", command=self.next_track).pack(side=tk.LEFT, padx=10)

        #self.update_now_playing()
        #threading.Thread(target=self.load_music_data, daemon=True).start()

	## Requires Auth Token not Client ##
        #tracks = self.fetch_playlist_tracks()
        tracks = self.fetch_top_tracks()

        for name, artist, image_url, link in tracks[:5]:  # show 5 tracks
            label = tk.Label(self.frame, text=f"{name} - {artist}", bg="white", font=("Arial", 12))
            label.pack()

            try:
                img_data = requests.get(image_url, timeout=5).content
                img = Image.open(BytesIO(img_data)).resize((100, 100))
                photo = ImageTk.PhotoImage(img)

                img_label = tk.Label(self.frame, image=photo, cursor="hand2", bg="white")
                img_label.image = photo  # prevent garbage collection
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
            except Exception as e:
                print(f"Failed to Load Image: {e}")
                tk.Label(self.frame, text="Image Failed to Load", bg="white").pack()

    def load_music_data(self):
        self.update_now_playing()
        tracks = self.fetch_playlist_tracks()
        self.display_tracks(tracks)

    def update_now_playing(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)

        if resp.status_code != 200:
            self.track_label.config(text="Nothing playing or not authorized.")
            return

        data = resp.json()
        track = data['item']
        name = track['name']
        artist = track['artists'][0]['name']
        album_url = track['album']['images'][0]['url']

        self.track_label.config(text=f"{name} - {artist}")

        img_data = requests.get(album_url, timeout=5).content
        img = Image.open(BytesIO(img_data)).resize((200, 200))
        self.album_img = ImageTk.PhotoImage(img)
        self.album_art_label.config(image=self.album_img)

    def play(self):
        requests.put("https://api.spotify.com/v1/me/player/play", headers={"Authorization": f"Bearer {self.token}"})

    def pause(self):
        requests.put("https://api.spotify.com/v1/me/player/pause", headers={"Authorization": f"Bearer {self.token}"})

    def next_track(self):
        requests.post("https://api.spotify.com/v1/me/player/next", headers={"Authorization": f"Bearer {self.token}"})
        #self.update_now_playing()
        threading.Thread(target=self.load_music_data, daemon=True).start()

    def get_spotify_token(client_id, client_secret):
        auth_str = f"{client_id}:{client_secret}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        headers = {"Authorization": f"Basic {b64_auth}"}
        data = {"grant_type": "client_credentials"}

        response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
        return response.json().get("access_token")

    def fetch_playlist_tracks(self):
            playlist_id = "37i9dQZF1DXcBWIGoYBM5M"  # Replace with your playlist ID
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            headers = {
                "Authorization": f"Bearer {self.token}"
            }

            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                print("Failed to fetch playlist:", resp.text)
                return []

            data = resp.json()
            tracks = []
            for item in data["items"]:
                track = item["track"]
                name = track["name"]
                artist = track["artists"][0]["name"]
                image_url = track["album"]["images"][0]["url"]
                external_url = track["external_urls"]["spotify"]
                tracks.append((name, artist, image_url, external_url))
            return tracks

    def fetch_top_tracks(self):
        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "q": "Today's Top Hits",
            "type": "track",
            "limit": 5
       }

        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print("Failed to fetch tracks:", resp.text)
            return []

        data = resp.json()
        tracks = []
        for item in data["tracks"]["items"]:
            name = item["name"]
            artist = item["artists"][0]["name"]
            image_url = item["album"]["images"][0]["url"]
            external_url = item["external_urls"]["spotify"]
            tracks.append((name, artist, image_url, external_url))
        return tracks

    def display_tracks(self, tracks):
        for name, artist, image_url, link in tracks[:5]:
            def render():
                label = tk.Label(self.frame, text=f"{name} - {artist}", bg="white", font=("Arial", 12))
                label.pack()

                try:
                    img_data = requests.get(image_url, timeout=5).content
                    img = Image.open(BytesIO(img_data)).resize((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(self.frame, image=photo, cursor="hand2", bg="white")
                    img_label.image = photo
                    img_label.pack()
                    img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
                except Exception as e:
                    print("Image load failed:", e)
                    fallback = tk.Label(self.frame, text="[Image not loaded]", bg="white")
                    fallback.pack()

            self.frame.after(0, render)

## NPR ##
def play_npr_stream():
    pygame.mixer.init()
    pygame.mixer.music.load("https://npr-ice.streamguys1.com/live.mp3")
    pygame.mixer.music.play()

def stop_npr_stream():
    pygame.mixer.music.stop()

## Music Page ##
class MusicApp:
    def __init__(self, root, backgroundImg, backImg, back_callback, token):
        self.root = root
        self.backgroundImg = backgroundImg
        self.backImg = backImg
        self.back_callback = back_callback
        self.token = token

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        self.npr_player = None

        self.create_ui()

    def create_ui(self):
        # Back button
        tk.Button(self.frame, image=self.backImg, command=self.back_callback).place(relx=0.05, rely=0.9)

        # --- Spotify Section ---
        self.track_label = tk.Label(self.frame, text="Loading Spotify info...", font=("Arial", 16), bg="white")
        self.track_label.pack(pady=10)

        self.album_art_label = tk.Label(self.frame, bg="white")
        self.album_art_label.pack(pady=10)

        controls = tk.Frame(self.frame, bg="white")
        controls.pack(pady=10)

        tk.Button(controls, text="Play",font=("Arial", 12), command=self.play_spotify).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Pause", command=self.pause_spotify).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Next", command=self.next_track).pack(side=tk.LEFT, padx=5)

        # --- NPR Section ---
        npr_controls = tk.Frame(self.frame, bg="white")
        npr_controls.pack(pady=20)

        tk.Label(npr_controls, text="NPR Radio", font=("Arial", 14), bg="white").pack()

        tk.Button(npr_controls, text="Play NPR", command=self.play_npr).pack(side=tk.LEFT, padx=10)
        tk.Button(npr_controls, text="Stop", command=self.stop_npr).pack(side=tk.LEFT, padx=10)

        #self.update_now_playing()
        threading.Thread(target=self.load_music_data, daemon=True).start()

    def load_music_data(self):
        self.update_now_playing()  # fetch and update current song
        tracks = self.fetch_playlist_tracks()  # fetch playlist
        self.display_tracks(tracks)  # safely update UI

    def display_tracks(self, tracks):
        for name, artist, image_url, link in tracks[:5]:
            def render():
                label = tk.Label(self.frame, text=f"{name} - {artist}", bg="white", font=("Arial", 12))
                label.pack()

                try:
                    img_data = requests.get(image_url, timeout=5).content
                    img = Image.open(BytesIO(img_data)).resize((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    img_label = tk.Label(self.frame, image=photo, cursor="hand2", bg="white")
                    img_label.image = photo  # prevent garbage collection
                    img_label.pack()
                    img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
                except Exception as e:
                    print("Image load failed:", e)
                    fallback = tk.Label(self.frame, text="[Image not loaded]", bg="white")
                    fallback.pack()

            self.frame.after(0, render)

    def update_now_playing(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        url = "https://api.spotify.com/v1/me/player/currently-playing"

        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                self.track_label.config(text="No Spotify playback available.")
                return

            data = resp.json()
            track = data.get("item")
            if not track:
                self.track_label.config(text="No song info available.")
                return

            name = track["name"]
            artist = track["artists"][0]["name"]
            album_img_url = track["album"]["images"][0]["url"]

            self.track_label.config(text=f"{name} - {artist}")

            img_data = requests.get(album_img_url, timeout=5).content
            img = Image.open(BytesIO(img_data)).resize((200, 200))
            self.album_img = ImageTk.PhotoImage(img)
            self.album_art_label.config(image=self.album_img)

        except Exception as e:
            self.track_label.config(text=f"Spotify error: {e}")

    def play_spotify(self):
        requests.put("https://api.spotify.com/v1/me/player/play", headers={"Authorization": f"Bearer {self.token}"})

    def pause_spotify(self):
        requests.put("https://api.spotify.com/v1/me/player/pause", headers={"Authorization": f"Bearer {self.token}"})

    def next_track(self):
        requests.post("https://api.spotify.com/v1/me/player/next", headers={"Authorization": f"Bearer {self.token}"})
        #self.update_now_playing()
        threading.Thread(target=self.load_music_data, daemon=True).start()

    def play_npr(self):
        if self.npr_player is None:
           self.npr_player = vlc.MediaPlayer("https://npr-ice.streamguys1.com/live.mp3")
        self.npr_player.play()
        print("NPR Stream Started.")

    def stop_npr(self):
        if self.npr_player:
           self.npr_player.stop()
           print("NPR Stream Stopped.")

    def fetch_playlist_tracks(self):
        playlist_id = "37i9dQZF1DXcBWIGoYBM5M"  # replace with your playlist
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            print("Failed to fetch playlist:", resp.text)
            return []

        data = resp.json()
        tracks = []
        for item in data["items"]:
            track = item["track"]
            name = track["name"]
            artist = track["artists"][0]["name"]
            image_url = track["album"]["images"][0]["url"]
            external_url = track["external_urls"]["spotify"]
            tracks.append((name, artist, image_url, external_url))
        return tracks

if __name__ == "__main__":
#  root = tk.Tk()
 #   root.geometry("1024x600")
 #   root.title("Pantry Server")

    # hide the main window until the splash is done
    root.withdraw()

    # show splash for 3.5s
    splash = SplashScreen(root, "pics/IntroGIF.gif", delay=3500)

    # after 3500ms, destroy the splash, show the main window, and launch the app exactly once
    def start_app():
        splash.destroy()
        root.deiconify()
        #ExpirationApp(root)
        ExpirationApp(root, spotify_token)

    root.after(3500, start_app)
    root.mainloop()
