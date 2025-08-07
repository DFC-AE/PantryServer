# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import simpledialog, messagebox, Button, Canvas, Label, Scrollbar, StringVar, OptionMenu, Tk, ttk, Frame, Button, Label
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
from urllib.parse import quote
## MultiThreading ##
import threading
## Web Browser ##
from tkhtmlview import HTMLLabel
import webview
## For System Fonts ##
import tkinter.font as tkFont
#from playsound import playsound

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
APP_FONT = tkFont.nametofont("TkDefaultFont")
APP_FONT_TITLE = tkFont.nametofont("TkDefaultFont")
APP_FONT_BOLD = ("TkDefaultFont", 12, "bold")
APP_FONT_TITLE_BOLD = ("TkDefaultFont", 30, "bold")
APP_FONT.configure(size=12)
APP_FONT_TITLE.configure(size=25)
CITY = "Shreveport, US"
KEY_WEATHER = "f63847d7129eb9be9c7a464e1e5ef67b"  # Your OpenWeatherMap API key
CONFIG_FILE = "config.json"
SAVE_FILE = "items.json"

### Import and Resize Button Images ###
## Button Size ##
img_wdt = 75
img_hgt = 75
## Add Image ##
img_add = Image.open("pics/icons/add.png")
img_add = img_add.resize((img_wdt, img_hgt), Image.LANCZOS)
addImg = ImageTk.PhotoImage(img_add)
## Back Image ##
img_back = Image.open("pics/icons/back.png")
img_back = img_back.resize((img_wdt, img_hgt), Image.LANCZOS)
backImg = ImageTk.PhotoImage(img_back)
## Camera Image ##
img_cam = Image.open("pics/icons/cam.jpg")
img_cam = img_cam.resize((img_wdt, img_hgt), Image.LANCZOS)
camImg = ImageTk.PhotoImage(img_cam)
## Card Image ##
img_card = Image.open("pics/icons/card4.png")
img_card = img_card.resize((img_wdt, img_hgt), Image.LANCZOS)
cardImg = ImageTk.PhotoImage(img_card)
## Light Image ##
img_light = Image.open("pics/icons/light.png")
img_light = img_light.resize((img_wdt, img_hgt), Image.LANCZOS)
lightImg = ImageTk.PhotoImage(img_light)
## Food Button Image ##
img_food = Image.open("pics/icons/food.jpg").resize((100, 100), Image.LANCZOS)
foodImg = ImageTk.PhotoImage(img_food)
## Home Image ##
img_home = Image.open("pics/icons/home.png")
img_home = img_home.resize((img_wdt, img_hgt), Image.LANCZOS)
homeImg = ImageTk.PhotoImage(img_home)
## Item Image ##
img_item = Image.open("pics/icons/item.png")
img_item = img_item.resize((img_wdt, img_hgt), Image.LANCZOS)
itemImg = ImageTk.PhotoImage(img_item)
## KLPI Button ##
img_klpi = Image.open("pics/icons/klpi.png").resize((50, 50), Image.LANCZOS)
klpiImg = ImageTk.PhotoImage(img_klpi)
## List Image ##
img_list = Image.open("pics/icons/list.png")
img_list = img_list.resize((img_wdt, img_hgt), Image.LANCZOS)
listImg = ImageTk.PhotoImage(img_list)
## Music Image ##
img_music = Image.open("pics/icons/music.png")
img_music = img_music.resize((img_wdt, img_hgt), Image.LANCZOS)
musicImg = ImageTk.PhotoImage(img_music)
## Music Background Image ##
img_music_back = Image.open("pics/backgrounds/music.jpg")
img_music_back = img_music_back.resize((img_wdt, img_hgt), Image.LANCZOS)
musicbackImg = ImageTk.PhotoImage(img_music_back)
## NPR Image ##
img_npr = Image.open("pics/icons/npr.png")
img_npr = img_npr.resize((img_wdt, img_hgt), Image.LANCZOS)
nprImg = ImageTk.PhotoImage(img_npr)
## Podcast Image ##
img_pod = Image.open("pics/icons/podcast.png").resize((100, 100), Image.LANCZOS)
podImg = ImageTk.PhotoImage(img_pod)
## Save Image ##
img_save = Image.open("pics/icons/save.jpg")
img_save = img_save.resize((img_wdt, img_hgt), Image.LANCZOS)
saveImg = ImageTk.PhotoImage(img_save)
## Scan Image ##
img_scan = Image.open("pics/icons/scan.jpg")
img_scan = img_scan.resize((img_wdt, img_hgt), Image.LANCZOS)
scanImg = ImageTk.PhotoImage(img_scan)
## Settings Image ##
img_set = Image.open("pics/icons/settings.png")
img_set = img_set.resize((img_wdt, img_hgt), Image.LANCZOS)
setImg = ImageTk.PhotoImage(img_set)
## Spotify Image ##
img_spot = Image.open("pics/icons/spot.png")
img_spot = img_spot.resize((img_wdt, img_hgt), Image.LANCZOS)
spotImg = ImageTk.PhotoImage(img_spot)
## View Image ##
img_view = Image.open("pics/icons/view.png")
img_view = img_view.resize((img_wdt, img_hgt), Image.LANCZOS)
viewImg = ImageTk.PhotoImage(img_view)
## Weather Image ##
img_weather = Image.open("pics/icons/weather.png")
img_weather = img_weather.resize((img_wdt, img_hgt), Image.LANCZOS)
weatherImg = ImageTk.PhotoImage(img_weather)
## Weather Background Image ##
img_back_weather = Image.open("pics/backgrounds/weather.jpg")
img_back_weather = img_back_weather.resize((img_wdt, img_hgt), Image.LANCZOS)
back_weatherImg = ImageTk.PhotoImage(img_back_weather)
## Clear Weather Background Image ##
img_back_day_clear = Image.open("pics/backgrounds/day_clear.jpg")
img_back_day_clear = img_back_day_clear.resize((img_wdt, img_hgt), Image.LANCZOS)
back_cleardayImg = ImageTk.PhotoImage(img_back_day_clear)
img_back_night_clear = Image.open("pics/backgrounds/night_clear.jpg")
img_back_night_clear = img_back_night_clear.resize((img_wdt, img_hgt), Image.LANCZOS)
back_clearnightImg = ImageTk.PhotoImage(img_back_night_clear)
## Cloudy Weather Background Image ##
img_back_day_cloudy = Image.open("pics/backgrounds/day_cloudy.jpg")
img_back_day_cloudy = img_back_day_cloudy.resize((img_wdt, img_hgt), Image.LANCZOS)
back_cloudydayImg = ImageTk.PhotoImage(img_back_day_cloudy)
img_back_night_cloudy = Image.open("pics/backgrounds/night_cloudy.jpg")
img_back_night_cloudy = img_back_night_cloudy.resize((img_wdt, img_hgt), Image.LANCZOS)
back_cloudynightImg = ImageTk.PhotoImage(img_back_night_cloudy)
## Rainy Weather Background Image ##
img_back_day_rainy = Image.open("pics/backgrounds/day_rainy.jpg")
img_back_day_rainy = img_back_day_rainy.resize((img_wdt, img_hgt), Image.LANCZOS)
back_rainydayImg = ImageTk.PhotoImage(img_back_day_rainy)
img_back_night_rainy = Image.open("pics/backgrounds/night_rainy.jpg")
img_back_night_rainy = img_back_night_rainy.resize((img_wdt, img_hgt), Image.LANCZOS)
back_rainynightImg = ImageTk.PhotoImage(img_back_night_rainy)
## Stormy Weather Background Image ##
img_back_day_stormy = Image.open("pics/backgrounds/day_stormy.jpg")
img_back_day_stormy = img_back_day_stormy.resize((img_wdt, img_hgt), Image.LANCZOS)
back_stormydayImg = ImageTk.PhotoImage(img_back_day_stormy)
img_back_night_stormy = Image.open("pics/backgrounds/night_stormy.jpg")
img_back_night_stormy = img_back_night_stormy.resize((img_wdt, img_hgt), Image.LANCZOS)
back_stormynightImg = ImageTk.PhotoImage(img_back_night_stormy)
## Snowy Weather Background Image ##
img_back_day_snowy = Image.open("pics/backgrounds/day_snowy.jpg")
img_back_day_snowy = img_back_day_snowy.resize((img_wdt, img_hgt), Image.LANCZOS)
back_snowydayImg = ImageTk.PhotoImage(img_back_day_snowy)
img_back_night_snowy = Image.open("pics/backgrounds/night_snowy.jpg")
img_back_night_snowy = img_back_night_snowy.resize((img_wdt, img_hgt), Image.LANCZOS)
back_snowynightImg = ImageTk.PhotoImage(img_back_night_snowy)
## Misty Weather Background Image ##
img_back_day_misty = Image.open("pics/backgrounds/day_misty.jpg")
img_back_day_misty = img_back_day_misty.resize((img_wdt, img_hgt), Image.LANCZOS)
back_mistydayImg = ImageTk.PhotoImage(img_back_day_misty)
img_back_night_misty = Image.open("pics/backgrounds/night_misty.jpg")
img_back_night_misty = img_back_night_misty.resize((img_wdt, img_hgt), Image.LANCZOS)
back_mistynightImg = ImageTk.PhotoImage(img_back_night_misty)
## Weather Back Button Image ##
img_back_small = Image.open("pics/icons/back.png").resize((50, 50), Image.LANCZOS)
backsmallImg = ImageTk.PhotoImage(img_back_small)
## Web Button Image ##
img_web = Image.open("pics/icons/web.png").resize((50, 50), Image.LANCZOS)
webImg = ImageTk.PhotoImage(img_web)
## YouTube Button Image ##
img_yt = Image.open("pics/icons/youtube.png").resize((50, 50), Image.LANCZOS)
ytImg = ImageTk.PhotoImage(img_yt)

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

# Start the webview event loop in a separate thread
#def start_webview_loop():
#    webview.create_window("Browser Placeholder", "https://example.com", hidden=True)
#    webview.start(debug=True)

#webview_thread = threading.Thread(target=start_webview_loop, daemon=True)
#webview_thread.start()

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
        self.load_items()
        self.clear_screen()
        self.items = []  # List to hold all items
        self.barcode = barcode = None
        self.current_view = 'home'
        self.dark_mode = False  # Track dark mode state
        self.sort_option = StringVar()
        self.sort_option.set("Sort By")
        self.backgroundImg = ImageTk.PhotoImage(Image.open("pics/backgrounds/back.jpg").resize((1024, 600), Image.LANCZOS))
        self.card_backgroundImg = ImageTk.PhotoImage(Image.open("pics/backgrounds/back_pastel.jpg").resize((1024, 600), Image.LANCZOS))
        self.list_backgroundImg = ImageTk.PhotoImage(Image.open("pics/backgrounds/back_toon.jpg").resize((1024, 600), Image.LANCZOS))
        #self.backImg = PhotoImage(file="pics/back.png")
        self.bg_color = "#f0f0f0"
        self.backImg = ImageTk.PhotoImage(Image.open("pics/icons/back.png").resize((50,50), Image.LANCZOS))
        self.init_camera()
        self.search_var = tk.StringVar()
        self.load_settings()
        self.apply_settings()
        self.create_home_screen()
#        self.weather_ui()

    ## Create Background ##
#    def set_background(self):
#        background = tk.Label(self.root, image=self.backgroundImg)
#        background.place(x=0, y=0, relwidth=1, relheight=1)
#        background.lower()

    def set_background(self, path=None):
        # Fallback to saved setting
        if not path:
            path = getattr(self, "current_background", "back")

        # Use default image for keyword "back"
        if path == "back":
            path = "pics/backgrounds/back.jpg"

        # Remove existing background label if needed
        if hasattr(self, "bg_label") and self.bg_label is not None and self.bg_label.winfo_exists():
            self.bg_label.destroy()

        # Handle color backgrounds
        if path.lower() in ["white", "black", "lightgray", "lightblue", "lightgreen"]:
            self.root.configure(bg=path)
            self.bg_label = None
        else:
            try:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Background image not found: {path}")

                self.bg_image_original = Image.open(path)
                self.backgroundImg = ImageTk.PhotoImage(self.bg_image_original)
                self.bg_label = tk.Label(self.root, image=self.backgroundImg)
                self.bg_label.image = self.backgroundImg
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()

                # Only bind resize once (optional guard)
                if not hasattr(self, "_resize_bound") or not self._resize_bound:
                    self.root.bind("<Configure>", self.on_resize)
                    self._resize_bound = True

            except Exception as e:
                print(f"Error loading background image: {e}")
                self.root.configure(bg="white")

    def set_background_old(self, path=None):
        # Fallback to saved setting
        if not path:
            path = getattr(self, "current_background", "back")

        # Use default image for keyword "back"
        if path == "back":
            path = "pics/backgrounds/back.jpg"

        # Remove existing background label if needed
        if hasattr(self, "bg_label") and self.bg_label is not None and self.bg_label.winfo_exists():
            self.bg_label.destroy()

        # Handle color backgrounds
        if path.lower() in ["white", "black", "lightgray", "lightblue", "lightgreen"]:
            self.root.configure(bg=path)
            self.bg_label = None
        else:
            try:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Background image not found: {path}")

                self.bg_image_original = Image.open(path)
                self.backgroundImg = ImageTk.PhotoImage(self.bg_image_original)
                self.bg_label = tk.Label(self.root, image=self.backgroundImg)
                self.bg_label.image = self.backgroundImg
                self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label.lower()

                # Only bind resize once (optional guard)
                if not hasattr(self, "_resize_bound") or not self._resize_bound:
                    self.root.bind("<Configure>", self.on_resize)
                    self._resize_bound = True

            except Exception as e:
                print(f"Error loading background image: {e}")
                self.root.configure(bg="white")

    def on_resize(self, event):
        self.update_background_image()

    def update_background_image(self):
        if hasattr(self, 'bg_image_original') and self.bg_image_original:
            width = self.root.winfo_width()
            height = self.root.winfo_height()

            resized_image = self.bg_image_original.resize((width, height), Image.LANCZOS)
            self.backgroundImg = ImageTk.PhotoImage(resized_image)

            if hasattr(self, 'bg_label') and self.bg_label is not None:
                try:
                    if self.bg_label.winfo_exists():
                        self.bg_label.config(image=self.backgroundImg)
                        self.bg_label.image = self.backgroundImg
                except tk.TclError:
                    pass

    def apply_settings(self):
        global APP_FONT
        APP_FONT = (self.current_font, 12)
        self.create_home_screen()

    def open_in_app_browser(self, url):
        # Get the current size of the Tkinter window
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # Hide the main Tkinter window
        self.root.withdraw()

        # Create the webview window with same size
        window = webview.create_window("Recipe", url, width=width, height=height)

        # When the browser closes, restore the main app
        def after_browser():
            self.root.deiconify()
            self.clear_screen()
            #self.create_home_screen()
            self.root.after(0, self.create_home_screen)

        # Start pywebview (must be on main thread)
        webview.start(func=after_browser, gui='gtk', debug=False)

    def open_camera_ui(self):
        self.clear_screen()
        CameraApp(self.root, self.backgroundImg, self.backImg, self.create_home_screen)

    def open_weather_ui(self):
        self.clear_screen()
        WeatherApp(root, backImg, self.create_home_screen)
        #WeatherApp(self.root, self.backgroundImg, backImg, self.create_home_screen)

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

    def open_music_web(self):
        #import webview
        #webview.create_window("Spotify Player", "https://open.spotify.com")
        #webview.start()

        self.clear_screen()

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        back_btn = tk.Button(frame, image=self.backImg, command=self.create_home_screen)
        back_btn.pack(anchor="nw", padx=10, pady=10)

        html = """
        <h2>OpenFoodFacts</h2>
        <a href='https://open.spotify.com'>Open Spotify in Browser</a>
        """
        label = HTMLLabel(frame, html=html)
        label.pack(padx=20, pady=20)

    def open_foodfacts(self):
        #self.root.withdraw()  # Hide the Tkinter app window
        self.root.destroy()  # Destory the Tkinter app window

        def on_closed():
            #self.root.deiconify()
            import tkinter as tk
            self.root = tk.Tk()
            self.root.title("Pantry Server")
            self.create_home_screen()
            #self.root.after(0, self.restore_home)

        window = webview.create_window(
            "OpenFoodFacts",
            "https://world.openfoodfacts.org/",
            width=1024,
            height=600
        )

        try:
           window.events.closed += on_closed
        except AttributError:
           pass

        webview.start()

        #def run_webview():
        #    try:
        #        window = webview.create_window(
        #            "OpenFoodFacts",
        #            "https://world.openfoodfacts.org/",
        #            width=1024,
        #            height=600
        #        )
        #        window.events.closed += on_closed
        #        webview.start(gui='qt')
        #    except Exception as e:
        #    #except AttributeError:
        #        print("Webview Error:", e)
        #        #print("Warning: Your version of pywebview does not support 'events.closed'.")
        #        # Fallback: just re-show the window after blocking start
        #        #webview.start()
        #        #self.root.deiconify()
        #        #self.create_home_screen()
        #        #return
        #        self.root.after(0, self.restore_home)

        #    #webview.start()

        #threading.Thread(target=run_webview, daemon=True).start()
        #run_webview()

    def restore_home(self):
        self.root.deiconify()
        self.create_home_screen()

    def create_conversion_table_panel(self, parent):
            from_unit_var = StringVar(value="ounces")
            to_unit_var = StringVar(value="cups")
            input_var = StringVar()
            result_var = StringVar()
            ingredient_var = StringVar(value="Water")

            # Densities in g/ml
            densities = {
                "Water": 1.0,
                "Flour": 0.593,
                "Sugar": 0.845,
                "Butter": 0.911,
                "Oil": 0.92,
                "Honey": 1.42,
                "Milk": 1.03
            }

            panel = tk.Frame(parent, bg="orange", bd=2, relief=tk.GROOVE)
            #panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
            panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

            tk.Label(panel, text="Unit Converter", font=APP_FONT, bg="white").pack(pady=(10, 5))

            inner = tk.Frame(panel, bg="white")
            inner.pack(padx=10, pady=10)

            # Ingredient dropdown
            tk.Label(inner, text="Ingredient:", bg="white").grid(row=0, column=0, sticky="w")
            ttk.Combobox(inner, textvariable=ingredient_var, values=list(densities.keys()), state="readonly", width=12).grid(row=0, column=1, sticky="w", pady=5)

            # From entry
            tk.Label(inner, text="Amount:", bg="white").grid(row=1, column=0, sticky="w")
            entry = tk.Entry(inner, textvariable=input_var, width=10)
            entry.grid(row=1, column=1, sticky="w", pady=5)

            # From unit
            ttk.Combobox(inner, textvariable=from_unit_var, values=["grams", "ounces", "cups"], state="readonly", width=10).grid(row=2, column=0, sticky="w", pady=5)
            # To unit
            ttk.Combobox(inner, textvariable=to_unit_var, values=["grams", "ounces", "cups"], state="readonly", width=10).grid(row=2, column=1, sticky="w", pady=5)

            # Result display
            tk.Label(inner, text="Converted:", bg="white").grid(row=3, column=0, sticky="w")
            result_entry = tk.Entry(inner, textvariable=result_var, state="readonly", width=15)
            result_entry.grid(row=3, column=1, sticky="w", pady=5)

            def convert_units(*_):
                try:
                    amt = float(input_var.get())
                    from_unit = from_unit_var.get()
                    to_unit = to_unit_var.get()
                    ingredient = ingredient_var.get()
                    density = densities.get(ingredient, 1)

                    # Convert input to grams
                    if from_unit == "grams":
                        grams = amt
                    elif from_unit == "ounces":
                        grams = amt * 28.3495
                    elif from_unit == "cups":
                        grams = amt * density * 240
                    else:
                        grams = amt

                    # Convert grams to output unit
                    if to_unit == "grams":
                        result = grams
                    elif to_unit == "ounces":
                        result = grams / 28.3495
                    elif to_unit == "cups":
                        result = grams / (density * 240)
                    else:
                        result = grams

                    result_var.set(f"{result:.2f}")
                except Exception:
                    result_var.set("Error")

            # Auto conversion on input or dropdown change
            input_var.trace_add("write", convert_units)
            from_unit_var.trace_add("write", convert_units)
            to_unit_var.trace_add("write", convert_units)
            ingredient_var.trace_add("write", convert_units)

    def create_conversion_table_panel_old(self, parent):
        panel = tk.Frame(parent, bg="", bd=2, relief=tk.GROOVE)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        title = tk.Label(panel, text="Unit Conversion", font=APP_FONT, bg="white")
        title.pack(pady=(10, 5))

        content = tk.Frame(panel, bg="white")
        content.pack(padx=10, pady=10)

        self.amount_var = tk.StringVar()
        self.unit_var = tk.StringVar(value="grams")
        self.result_var = tk.StringVar()

        tk.Entry(content, textvariable=self.amount_var, width=10).grid(row=0, column=0, padx=5)
        ttk.Combobox(
            content,
            textvariable=self.unit_var,
            values=["grams", "ounces", "sugar", "flour", "butter"],
            width=10
        ).grid(row=0, column=1, padx=5)

        tk.Button(content, text="Convert", command=self.convert_units).grid(row=0, column=2, padx=5)
        tk.Label(content, textvariable=self.result_var, bg="white", font=APP_FONT).grid(
            row=1, column=0, columnspan=3, pady=10
        )

    def convert_units(self):
        try:
            amount = float(self.amount_var.get())
            unit = self.unit_var.get().lower()

            conversions = {
                "grams": lambda x: f"{x / 28.35:.2f} oz",
                "ounces": lambda x: f"{x * 28.35:.2f} g",
                "sugar": lambda x: f"{x / 200:.2f} cups",
                "flour": lambda x: f"{x / 120:.2f} cups",
                "butter": lambda x: f"{x / 227:.2f} cups",
            }

            if unit in conversions:
                result = conversions[unit](amount)
            else:
                result = "Unsupported unit"

            self.result_var.set(result)
        except ValueError:
            self.result_var.set("Enter a valid number")

    def create_home_screen(self, item=None):
    #    for widget in self.root.winfo_children():
    #        widget.destroy()

        self.clear_screen()

        #def set_background(self):
     #   bg_label = tk.Label(self.root, image=self.backgroundImg)
     #   bg_label.place(x=0, y=0, relwidth=1, relheight=1)
     #   bg_label.lower()

        self.set_background()
        self.current_view = 'home'

       # Create top-left frame for weather icon
        self.weather_icon_frame = tk.Frame(self.root, bg="orange")
        self.weather_icon_frame.place(x=10, y=10)

        # Top area with clock and weather
        self.clock_label = tk.Label(self.root, font=APP_FONT_TITLE_BOLD,
                                    background='orange', foreground='yellow')
        self.clock_label.pack(pady=(10, 0))

        self.weather_label = tk.Label(self.root, font=APP_FONT_TITLE,
                                      bg='orange', fg='yellow')
        self.weather_label.pack(pady=(0, 10))

        # Middle frame for side panels (Expiring Soon and Conversion)
        middle_frame = tk.Frame(self.root, bg="")
        #middle_frame.pack(fill=tk.X, padx=10)
        middle_frame.pack(fill=tk.BOTH, expand=True)

        self.create_expiring_soon_panel(middle_frame)   # LEFT
        self.create_random_recipe_panel(middle_frame)      # MIDDLE
        self.create_conversion_table_panel(middle_frame)  # RIGHT

        self.populate_expiring_items()

        def update_clock():
            string = strftime("%A, %B %d %Y %H:%M:%S")
            if hasattr(self,'clock_label') and self.clock_label.winfo_exists():
                self.clock_label.config(text=string)
                self.root.after(1000, update_clock)

        update_clock()

        def update_weather():
            try:
                city = "Shreveport,US"
                api_key = "f63847d7129eb9be9c7a464e1e5ef67b"
                url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"

                response = requests.get(url)
                data = response.json()

                temp = data["main"]["temp"]
                condition = data["weather"][0]["description"].capitalize()
                icon_code = data["weather"][0]["icon"]
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

                icon_response = requests.get(icon_url)
                icon_img = Image.open(BytesIO(icon_response.content))
                icon_photo = ImageTk.PhotoImage(icon_img)

                if not hasattr(self, "weather_icon_label") or not self.weather_icon_label.winfo_exists():
                    #self.weather_icon_label = tk.Label(self.weather_icon_frame, bg="orange")
                    #self.weather_icon_label.pack()
                    self.weather_button = tk.Button(
                         self.weather_icon_frame,
                         image=icon_photo,
                         bg="orange",
                         #bd=0,                 # no border
                         #highlightthickness=0, # no highlight border
                         command=self.open_weather_ui
                    )
                    self.weather_button.image = icon_photo
                    self.weather_button.pack()
                else:
                    self.weather_button.config(image=icon_photo)
                    self.weather_button.image = icon_photo

                if not hasattr(self, "weather_label") or not self.weather_label.winfo_exists():
                    self.weather_label = tk.Label(
                        self.root,
                        font=APP_FONT,
                        bg="orange",
                        fg="yellow"
                    )

                    self.weather_label.pack(pady=(0, 10))
                #self.update_weather()

                #self.weather_icon_label.config(image=icon_photo)
                #self.weather_icon_label.image = icon_photo  # Prevent GC

                self.weather_label.config(
                    text=f"{city.split(',')[0]}: {temp:.1f}\u00b0F, {condition}"
                )

            except tk.TclError:
                print("Weather Widget Destroyed - Stopping Update.")
            except Exception as e:
                print("Weather fetch error:", e)
                if hasattr(self, "weather_label"):
                    self.weather_label.config(text="Weather: Unable to load")

            self.root.after(600000, update_weather)

        update_weather()

        # Enlarged calendar
        #self.cal = Calendar(self.root, selectmode='day', date_pattern="yyyy-mm-dd", background="orange", foreground="yellow", font=('calibri', 15, 'bold'), cursor="hand2")
        #self.cal.pack(pady=(5, 10), ipady=10, ipadx=10)

#        calendar_frame = tk.Frame(middle_frame, bg="", bd=2, relief=tk.GROOVE)
#        calendar_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

#        self.cal = Calendar(
#            middle_frame,
#            selectmode='day',
#            date_pattern="yyyy-mm-dd",
#            font=APP_FONT,
#            background="orange",
#            disabledbackground="orange",
#            bordercolor="orange",
#            headersbackground="orange",
#            normalbackground="white",
#            weekendbackground="lightyellow",
#            othermonthwebackground="lightgray",
#            othermonthbackground="white"
#        )
#        self.cal.pack(side=tk.LEFT, padx=10, pady=10, ipadx=20, ipady=20)

        #self.cal = Calendar(calendar_frame, selectmode='day', date_pattern="yyyy-mm-dd",
        #            background="orange", disabledbackground="orange",
        #            bordercolor="gray", headersbackground="orange", normalbackground="white")
        #self.cal.pack(padx=10, pady=10, ipadx=5, ipady=5)

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

        web_btn = tk.Button(button_frame, cursor="hand2", image=webImg, width=100, height=100, command=lambda: self.open_foodfacts())
        web_btn.pack(side=tk.RIGHT)
        ToolTip(web_btn, "Click to Open Web Browser")

        spot_btn = tk.Button(button_frame, cursor="hand2", image=spotImg, width=100, height=100, command=lambda: self.open_spotify_ui())
        spot_btn.pack(side=tk.RIGHT)
        ToolTip(spot_btn, "Click to Open Spotify")

        dark_mode_btn = tk.Button(button_frame, cursor="hand2", image=lightImg, width=100, height=100, command=self.toggle_dark_mode)
        dark_mode_btn.pack(side=tk.LEFT)
        ToolTip(dark_mode_btn, "Click to Toggle Light/Dark Mode Test")

        set_btn = tk.Button(button_frame, cursor="hand2", image=setImg, width=100, height=100, command=lambda: self.open_settings_page())
        set_btn.pack(side=tk.LEFT)
        ToolTip(set_btn, "Click to Configure Application")

        #refresh_btn = tk.Button(button_frame, cursor="hand2", image=foodImg, command=self.load_random_recipe)
        #refresh_btn.image = foodImg
        #refresh_btn.pack(side=tk.LEFT)
        #ToolTip(refresh_btn, "Click to Generate a New Random Recipe")

        # To unit dropdown
        self.to_unit = tk.StringVar(value="ounces")

        # Conversion logic
        self.unit_factors = {
            ("grams", "ounces"): lambda x: x * 0.0353,
            ("ounces", "grams"): lambda x: x / 0.0353,
            ("sugar", "grams"): lambda x: x * 200,
            ("flour", "grams"): lambda x: x * 120,
            ("butter", "grams"): lambda x: x * 227,
            ("grams", "sugar"): lambda x: x / 200,
            ("grams", "flour"): lambda x: x / 120,
            ("grams", "butter"): lambda x: x / 227,
        }

        def perform_conversion():
            try:
                val = float(self.convert_input.get())
                from_u = self.from_unit.get()
                to_u = self.to_unit.get()
                if from_u == to_u:
                    result = val
                else:
                    result = self.unit_factors.get((from_u, to_u), lambda x: "N/A")(val)
                self.convert_result.config(text=f"= {round(result, 2)} {to_u}")
            except:
                self.convert_result.config(text="")

        self.perform_conversion = perform_conversion

        for widget in self.root.winfo_children():
            widget.lift()

    def create_expiring_soon_panel(self, parent):
        panel = tk.Frame(parent, bg="orange", bd=2, relief=tk.GROOVE, width=300)
        #panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        #panel.pack_propagate(False)

        title = tk.Label(panel, text="Expiring Soon", font=APP_FONT, bg="white")
        title.pack(pady=(10, 5))

        list_frame = tk.Frame(panel, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True)

        canvas = Canvas(list_frame, bg="white", highlightthickness=0)
        scrollbar = Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")
        self.expiring_frame = scrollable_frame

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def populate_expiring_items(self):
        for widget in self.expiring_frame.winfo_children():
            widget.destroy()

        from datetime import datetime, timedelta
        today = datetime.today()
        soon = today + timedelta(days=3)

        expiring_items = [
            item for item in self.items
            if item.expiration_date and item.expiration_date <= soon
        ]

        if not expiring_items:
            tk.Label(self.expiring_frame, text="No items expiring soon.",
                     font=APP_FONT, bg="white", fg="gray").pack(pady=10)
        else:
            for item in expiring_items:
                name = item.name
                expiry = item.expiration_date.strftime("%Y-%m-%d")
                days_left = (item.expiration_date - today).days

                # Color code
                if days_left <= 0:
                    color = "red"
                elif days_left == 1:
                    color = "orange"
                else:
                    color = "green"

                label = tk.Label(self.expiring_frame,
                                 text=f"{name} (expires in {days_left} day{'s' if days_left != 1 else ''})",
                                 font=APP_FONT, bg="white", fg=color, anchor="w", justify="left")
                label.pack(fill=tk.X, padx=10, pady=5)

    def create_random_recipe_panel(self, parent):
        panel = tk.Frame(parent, bg="orange", bd=2, relief=tk.GROOVE, width=300, height=300)
        #panel.pack(side=tk.LEFT, padx=10, pady=10)
        panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        #panel.pack_propagate(False)

        title = tk.Label(panel, text="Random Recipe", font=APP_FONT, bg="white")
        title.pack(pady=(10, 5))

        # Recipe image
        self.recipe_image_label = tk.Label(panel, bg="white")
        self.recipe_image_label.pack(pady=5)

        # Recipe name
        self.recipe_name_label = tk.Label(panel, text="", font=APP_FONT,
                                          bg="white", wraplength=250)
        self.recipe_name_label.pack(pady=5)

        # Link to full recipe
        self.recipe_link_label = tk.Label(panel, text="View Recipe", fg="blue",
                                          cursor="hand2", bg="white")
        self.recipe_link_label.pack(pady=5)
        #self.recipe_link_label.bind("<Button-1>", lambda e: webbrowser.open(self.recipe_url))
        self.recipe_link_label.bind("<Button-1>", lambda e: self.open_in_app_browser(self.recipe_url))

        # Refresh button
        #refresh_btn = tk.Button(panel, cursor="hand2", image="refreshImg", command=self.load_random_recipe)
        refresh_btn = tk.Button(panel, cursor="hand2", image=foodImg, command=self.load_random_recipe)
        refresh_btn.pack(pady=5)
        ToolTip(refresh_btn, "Click to Load a New Recipe")

            # Load the first recipe
        self.load_random_recipe()
        #self.load_random_recipe(self.current_recipe = meal)

    def load_random_recipe(self):
        try:
            response = requests.get("https://www.themealdb.com/api/json/v1/1/random.php", timeout=5)
            data = response.json()

            meal = data["meals"][0]
            self.current_recipe = meal

            name = meal["strMeal"]
            image_url = meal["strMealThumb"]
            instructions = meal["strSource"] or f"https://www.themealdb.com/meal/{meal['idMeal']}"

            self.recipe_name_label.config(text=name)

            # Bind click event on image to open detail view
            #self.recipe_image_label.bind("<Button-1>", lambda e: self.show_full_recipe_view())
            self.recipe_image_label.bind("<Button-1>", lambda e: self.show_full_recipe_view(self.current_recipe))
            self.recipe_image_label.config(cursor="hand2")

            self.recipe_link_label.config(text="View Recipe", fg="blue", cursor="hand2")
            #self.recipe_link_label.bind("<Button-1>", lambda e: webbrowser.open(instructions))
            #self.recipe_link_label.bind("<Button-1>", lambda e: self.open_in_app_browser(self.recipe_url))
            self.recipe_link_label.bind("<Button-1>", lambda e: self.open_in_app_browser(instructions))

            img_data = requests.get(image_url, timeout=5).content
            img = Image.open(BytesIO(img_data)).resize((200, 200))
            photo = ImageTk.PhotoImage(img)
            self.recipe_image_label.config(image=photo)
            self.recipe_image_label.image = photo  # Prevent GC

        except Exception as e:
            self.recipe_name_label.config(text="Failed to load recipe.")
            self.recipe_link_label.config(text="")
            self.recipe_image_label.config(image='')

    def show_full_recipe_view(self, meal):
        self.clear_screen()
        rating = round(random.uniform(3.5, 5.0), 1)

        # Create scrollable canvas
        canvas = tk.Canvas(self.root, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="white")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Back button
        back_btn = tk.Button(scrollable_frame, image=self.backImg, command=self.create_home_screen, bg="white", bd=0)
        back_btn.pack(pady=10, anchor="w", padx=10)

        ## New ##
        # Horizontal container for image and text
        content_frame = tk.Frame(scrollable_frame, bg="white")
        content_frame.pack(fill=tk.X, padx=10, pady=10)

        # Meal image (LEFT)
        try:
            image_url = meal["strMealThumb"]
            img_data = requests.get(image_url, timeout=5).content
            img = Image.open(BytesIO(img_data)).resize((200, 200))
            photo = ImageTk.PhotoImage(img)

            self.recipe_full_image_label = tk.Label(content_frame, image=photo, bg="white")
            self.recipe_full_image_label.image = photo  # Prevent GC
            self.recipe_full_image_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print("Error loading image:", e)

        # Text content (RIGHT)
        text_frame = tk.Frame(content_frame, bg="white")
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Vertically center the text content using stretch and expand
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        text_inner = tk.Frame(text_frame, bg="white")
        text_inner.pack(expand=True)

        tk.Label(text_inner, text=meal["strMeal"], font=APP_FONT_BOLD,
                 bg="white", anchor="w").pack(anchor="w", pady=(0, 5))

        tk.Label(text_inner, text=f"Category: {meal['strCategory']}   Rating: {rating:.1f} ",
                 font=APP_FONT, bg="white", anchor="w").pack(anchor="w")

        ## Meal name
#        tk.Label(scrollable_frame, text=meal["strMeal"], font=APP_FONT_BOLD, bg="white").pack(pady=10)

        ## Category and rating (simulated rating)
        #rating = "4/5"
#        rating = random.uniform(3.5, 5.0)
#        tk.Label(scrollable_frame, text=f"Category: {meal['strCategory']}   {rating}",
#                 font=APP_FONT, bg="white").pack(pady=5)

        tk.Label(scrollable_frame, text="Ingredients:", font=APP_FONT, bg="white").pack(pady=5)
        for i in range(1, 21):
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                tk.Label(scrollable_frame, text=f" {ingredient} - {measure}",
                         font=APP_FONT, bg="white", anchor="w", justify="left").pack(fill=tk.X, padx=20)

        # Instructions
        tk.Label(scrollable_frame, text="Instructions:", font=APP_FONT, bg="white").pack(pady=(10, 5))
        tk.Label(scrollable_frame, text=meal["strInstructions"], wraplength=700, justify="left",
                 font=APP_FONT, bg="white").pack(padx=20, pady=5)

        # Print & PDF export buttons
        button_frame = tk.Frame(scrollable_frame, bg="white")
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Save to Favorites", command=lambda: self.save_recipe_favorite(meal)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Print", command=lambda: self.print_recipe(meal)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export to PDF", command=lambda: self.export_recipe_to_pdf(meal)).pack(side=tk.LEFT, padx=5)

    def save_to_favorites(self, meal):
        # Save logic (e.g., append to a JSON file)
        print("Saved:", meal["strMeal"])

    def print_recipe(self, meal):
        print("Print requested for:", meal["strMeal"])

    def export_to_pdf(self, meal):
        print("Export to PDF for:", meal["strMeal"])

    def show_full_recipe_view_old(self):
        if not hasattr(self, "current_recipe") or not self.current_recipe:
            return

        self.clear_screen()

        meal = self.current_recipe
        name = meal["strMeal"]
        instructions = meal["strInstructions"]
        image_url = meal["strMealThumb"]

        # Background
        bg_label = tk.Label(self.root, image=self.card_backgroundImg)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()

        # Title
        tk.Label(self.root, text=name, font=APP_FONT_BOLD, bg="white").pack(pady=10)

        # Image
        img_data = requests.get(image_url, timeout=5).content
        img = Image.open(BytesIO(img_data)).resize((300, 300))
        photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(self.root, image=photo, bg="white")
        img_label.image = photo
        img_label.pack(pady=10)

        # Instructions (scrollable)
        frame = tk.Frame(self.root)
        frame.pack(pady=10, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame, height=200, bg="white")
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        tk.Label(scroll_frame, text=instructions, bg="white", wraplength=700, justify="left").pack(padx=10, pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Back button
        back_btn = tk.Button(self.root, image=self.backImg, command=self.create_home_screen, cursor="hand2")
        back_btn.pack(pady=10)

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    self.current_font = config.get("font", "Arial")
                    self.current_background = config.get("background", "white")
                    self.current_icon = config.get("icon", "Icon1.png")
                    self.dark_mode = config.get("dark_mode", False)
            except Exception as e:
                print("Failed to load config:", e)
                self.set_default_settings()
        else:
            self.set_default_settings()

    def save_settings_to_file(self):
        config = {
            "font": self.current_font,
            "background": self.current_background,
            "icon": self.current_icon,
            "dark_mode": self.dark_mode
        }
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print("Failed to save config:", e)

    def set_default_settings(self):
        self.current_font = "Arial"
        self.current_background = "white"
        self.current_icon = "Icon1.png"
        self.dark_mode = False

    def apply_settings(self):
        global APP_FONT
        APP_FONT = (self.current_font, 12)
        self.create_home_screen()

    def open_settings_page(self):
        self.clear_screen()

        # Apply dynamic background based on current setting or default
        background_path = self.current_background
        if background_path == "back":
            background_path = "pics/backgrounds/settings.jpg"
        elif not os.path.exists(background_path) and not background_path.endswith(".jpg"):
            background_path = f"pics/backgrounds/{background_path}.jpg"

        self.set_background(background_path)

        # Title
        tk.Label(self.root, text="Settings", font=(self.current_font, 20, "bold"),
                 bg="white", pady=10).pack()

        frame = tk.Frame(self.root, padx=20, pady=20, bg="")
        frame.pack(fill=tk.BOTH, expand=True)

        # Font selection
        tk.Label(frame, text="Select Font:", font=(self.current_font, 14), bg="white").grid(row=0, column=0, sticky="w")
        fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "TkDefaultFont"]
        self.font_var = tk.StringVar(value=self.current_font)
        font_menu = tk.OptionMenu(frame, self.font_var, *fonts, command=self.preview_settings)
        font_menu.grid(row=0, column=1, sticky="ew")

        # Background selection
        tk.Label(frame, text="Select Background Theme:", font=(self.current_font, 14), bg="white").grid(row=1, column=0, sticky="w")
        backgrounds = ["back.jpg", "settings.jpg", "white", "lightgray", "lightblue", "lightgreen", "black"]
        self.bg_var = tk.StringVar(value=self.current_background)
        bg_menu = tk.OptionMenu(frame, self.bg_var, *backgrounds, command=self.preview_settings)
        bg_menu.grid(row=1, column=1, sticky="ew")

        # Icon selection
        tk.Label(frame, text="Select Icon Image:", font=(self.current_font, 14), bg="white").grid(row=2, column=0, sticky="w")
        icons = ["Icon1.png", "Icon2.png", "Icon3.png"]
        self.icon_var = tk.StringVar(value=self.current_icon)
        icon_menu = tk.OptionMenu(frame, self.icon_var, *icons, command=self.preview_settings)
        icon_menu.grid(row=2, column=1, sticky="ew")

        # Dark/Light mode toggle
        tk.Label(frame, text="Dark Mode:", font=(self.current_font, 14), bg="white").grid(row=3, column=0, sticky="w")
        self.dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        dark_toggle = tk.Checkbutton(frame, variable=self.dark_mode_var, command=self.preview_settings, bg="white")
        dark_toggle.grid(row=3, column=1, sticky="w")

        # Live preview label
        self.preview_label = tk.Label(frame, text="Sample Text", font=(self.font_var.get(), 14),
                                      bg=self.bg_var.get() if self.bg_var.get() in ["white", "black", "lightgray"] else "white")
        self.preview_label.grid(row=4, column=0, columnspan=2, pady=20)

        # Buttons
        button_frame = tk.Frame(frame, bg="white")
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        save_btn = tk.Button(button_frame, text="Save", command=self.save_settings_and_apply)
        save_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.create_home_screen)
        cancel_btn.pack(side=tk.LEFT, padx=10)

    def preview_settings(self, *_):
        font = self.font_var.get()
        bg = self.bg_var.get()
        icon = self.icon_var.get()
        dark = self.dark_mode_var.get()

        # Update label preview
        self.preview_label.config(font=(font, 14))

        if bg in ["white", "black", "lightgray", "lightblue", "lightgreen"]:
            self.preview_label.config(bg=bg)

        # Live background update if theme was changed
        bg_path = bg
        if bg == "settings":
            bg_path = "pics/backgrounds/settings.jpg"
        elif not os.path.exists(bg_path) and not bg_path.endswith(".jpg"):
            bg_path = f"pics/backgrounds/{bg}.jpg"

        if os.path.exists(bg_path):
            self.set_background(bg_path)

    def save_settings_and_apply(self):
        self.current_font = self.font_var.get()
        self.current_background = self.bg_var.get()
        self.current_icon = self.icon_var.get()
        self.dark_mode = self.dark_mode_var.get()

        self.save_settings_to_file()
        self.apply_settings()

    def open_settings_page_old(self):
        self.clear_screen()

        # Apply dynamic background based on current setting or default
        background_path = self.current_background
        if background_path == "back":
            background_path = "pics/backgrounds/settings.jpg"

        self.set_background(background_path)

        # Title
        tk.Label(self.root, text="Settings", font=(self.current_font, 20, "bold"),
             bg="white", pady=10).pack()

        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Font selection
        tk.Label(frame, text="Select Font:", font=(self.current_font, 14)).grid(row=0, column=0, sticky="w")
        fonts = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Verdana", "TkDefaultFont"]
        self.font_var = tk.StringVar(value=self.current_font)
        font_menu = tk.OptionMenu(frame, self.font_var, *fonts, command=self.preview_settings)
        font_menu.grid(row=0, column=1, sticky="ew")

        # Background selection
        tk.Label(frame, text="Select Background Color:", font=(self.current_font, 14)).grid(row=1, column=0, sticky="w")
        backgrounds = ["white", "lightgray", "lightblue", "lightgreen", "black"]
        self.bg_var = tk.StringVar(value=self.current_background)
        bg_menu = tk.OptionMenu(frame, self.bg_var, *backgrounds, command=self.preview_settings)
        bg_menu.grid(row=1, column=1, sticky="ew")

        # Icon selection
        tk.Label(frame, text="Select Icon Image:", font=(self.current_font, 14)).grid(row=2, column=0, sticky="w")
        icons = ["Icon1.png", "Icon2.png", "Icon3.png"]
        self.icon_var = tk.StringVar(value=self.current_icon)
        icon_menu = tk.OptionMenu(frame, self.icon_var, *icons, command=self.preview_settings)
        icon_menu.grid(row=2, column=1, sticky="ew")

        # Dark/Light mode toggle
        tk.Label(frame, text="Dark Mode:", font=(self.current_font, 14)).grid(row=3, column=0, sticky="w")
        self.dark_mode_var = tk.BooleanVar(value=self.dark_mode)
        dark_toggle = tk.Checkbutton(frame, variable=self.dark_mode_var, command=self.preview_settings)
        dark_toggle.grid(row=3, column=1, sticky="w")

        # Live preview area
        preview_frame = tk.Frame(self.root, bd=1, relief=tk.SUNKEN, padx=10, pady=10)
        preview_frame.pack(pady=20, fill=tk.X, padx=20)

        self.preview_label = tk.Label(preview_frame, text="Preview Text",
                                      font=(self.current_font, 16),
                                      bg=self.current_background,
                                      fg="black" if not self.dark_mode else "white",
                                      width=30, height=5)
        self.preview_label.pack()

        # Save and Cancel buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        save_btn = tk.Button(btn_frame, text="Save Settings", command=self.save_settings)
        save_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.create_home_screen)
        cancel_btn.pack(side=tk.LEFT, padx=10)

        # Initial preview update
        self.preview_settings()

    def preview_settings(self, *args):
        font_choice = self.font_var.get()
        bg_choice = self.bg_var.get()
        dark = self.dark_mode_var.get()

        fg_color = "white" if dark else "black"

        self.preview_label.config(
            font=(font_choice, 16),
            bg=bg_choice,
            fg=fg_color,
            text=f"Font: {font_choice}\nBackground: {bg_choice}\nDark Mode: {'On' if dark else 'Off'}"
        )

    def save_settings(self):
        self.current_font = self.font_var.get()
        self.current_background = self.bg_var.get()
        self.current_icon = self.icon_var.get()
        self.dark_mode = self.dark_mode_var.get()

        # Apply and save to config file
        self.apply_settings()
        self.save_settings_to_file()
        self.create_home_screen()

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

        self.bg_image_original = Image.open("pics/backgrounds/back_pastel.jpg")
        self.bg_label = tk.Label(self.root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.update_background_image()
        self.bg_label.lower()
        self.root.bind("<Configure>", self.on_resize)

        # Set specific background for card view
        #bg_label = tk.Label(self.root, image=self.card_backgroundImg)
        #bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        #bg_label.lower()

        self.current_view = "card"

        # Search bar
        search_frame = tk.Frame(self.root, bg="")
        search_frame.pack(pady=(10, 0))

        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(10, 5))
        search_entry.bind("<KeyRelease>", lambda event: self.create_card_view())

        # Sort menu
        sort_menu = OptionMenu(self.root, self.sort_option, "Expiration (Soonest)", "Expiration (Latest)", "Name (A-Z)", "Name (Z-A)", command=self.sort_items)
        sort_menu.pack(pady=10)

        # Setup scrollable canvas
        #canvas = tk.Canvas(self.root, height=450, bg="SystemButtonFace", highlightthickness=0, bd=0)
        canvas = tk.Canvas(self.root, height=450, bg="lightgray", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        #scroll_frame = tk.Frame(canvas, bg="SystemButtonFace")
        scroll_frame = tk.Frame(canvas, bg="")


        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=self.root["bg"])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        search_term = self.search_var.get().lower().strip()

        row = col = 0
        for item in self.items:
            if search_term and search_term not in item.name.lower():
                continue  # Skip items that don't match search

            color = item.get_color()
            days = item.days_until_expired()
            text = f"{item.name} - Expires in {check_dates(days)} days" if days >= 0 else f"{item.name} - Expired"

            c_btn = tk.Button(
               scroll_frame, text=text, bg=color, fg="black", font=APP_FONT, wraplength=150,
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
        ToolTip(card_back_btn, "Click to Return to the Previous Screen")

    def create_list_view(self):
        self.clear_screen()
        self.current_view = "list"

        self.bg_image_original = Image.open("pics/backgrounds/back_toon.jpg")
        self.bg_label = tk.Label(self.root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.update_background_image()
        self.bg_label.lower()
        self.root.bind("<Configure>", self.on_resize)

        # Background image
        #bg_label = tk.Label(self.root, image=self.list_backgroundImg)
        #bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        #bg_label.lower()

        # Sort menu
        sort_menu = OptionMenu(self.root, self.sort_option, "Expiration (Soonest)", "Expiration (Latest)")
        sort_menu.pack(pady=5)

        # Search bar frame
        search_frame = tk.Frame(self.root, bg="")
        search_frame.pack(pady=5)

        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", lambda event: self.create_list_view())

        tk.Button(search_frame, text="Clear", command=lambda: self.clear_search(self.create_list_view)).pack(side=tk.LEFT)

        # Scrollable canvas
        canvas = tk.Canvas(self.root, height=450, bg="lightgray", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set, bg=self.root["bg"])

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Search filtering
        search_term = self.search_var.get().lower().strip()

        for item in self.items:
            if search_term and search_term not in item.name.lower():
                continue

            frame = tk.Frame(scroll_frame, bg=self.root["bg"])
            frame.pack(fill=tk.X, pady=2)

            color = item.get_color()
            days = item.days_until_expired()
            text = f"{item.name} - Expires in {check_dates(days)} days" if days >= 0 else f"{item.name} - Expired"
            tk.Label(frame, text=text, bg=color, fg="black", font=APP_FONT).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Button(frame, text="Delete", command=lambda i=item: self.delete_item(i)).pack(side=tk.RIGHT)

        # Back button
        back_btn = tk.Button(self.root, cursor="hand2", image=backImg, command=lambda: self.create_tracker_ui(None))
        back_btn.pack(pady=10)
        ToolTip(back_btn, "Click to Return to the Previous Screen")

    def refresh_list(self):
        self.create_list_view()

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

            tk.Label(nutrition_frame, text="Nutrition Facts:", font=APP_FONT, anchor="w", justify="left").pack(anchor="w")

            for key, value in item.nutrition_info.items():
                fact = f"{key}: {value}"
                tk.Label(nutrition_frame, text=fact, font=APP_FONT, anchor="w", justify="left").pack(anchor="w")


        label = tk.Label(self.root, text=detail_text, font=APP_FONT, justify="left")
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
        label_code = tk.Label(self.root, text="Enter Barcode Number:", font=APP_FONT, justify="center")
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

        upscale_factor = 2  # Try 2x or 3x
        frame_upscaled = cv2.resize(frame, (0, 0), fx=upscale_factor, fy=upscale_factor)

        barcodes = decode(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))

        for barcode in barcodes:
            data = barcode.data.decode("utf-8")
            barcode_type = barcode.type
            self.barcode_entry.delete(0, tk.END)
            self.barcode_entry.insert(0, data)
            self.barcode_label.config(text=f"Detected: {data}")
            self.beep_and_flash()
            print(f"Detected Barcode: {barcode_type} - {data}")

            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, data, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert to ImageTk
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(frame_rgb)
        #imgtk = ImageTk.PhotoImage(image=img_pil)
        self.imgtk = ImageTk.PhotoImage(image=img_pil)
        self.video_label.configure(image=self.imgtk)

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
            label = tk.Label(info_window, text=f"{key}: {value}", font=APP_FONT, anchor="w")
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

    def load_items(self):
        self.items = []
        if os.path.exists("items.json"):
            try:
                with open("items.json", "r") as f:
                    data = json.load(f)
                    for item in data:
                        # Adjust field names to match your JSON structure
                        name = item.get("name")
                        expiry_str = item.get("expiration_date")
                        if expiry_str:
                            # Ensure expiry_str is a string before parsing
                            if isinstance(expiry_str, datetime):
                                expiry = expiry_str
                            else:
                                expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
                            self.items.append(Item(name, expiry))
            except Exception as e:
                print(f"[Error] Failed to load items.json: {e}")
        else:
            print("[Info] items.json does not exist.")

    def save_items(self):
        try:
            with open("items.json", "w") as f:
                json.dump(
                    [{"name": item.name, "expiration_date": item.expiration_date.strftime("%Y-%m-%d")}
                     for item in self.items],
                    f,
                    indent=2
                )
        except Exception as e:
            print(f"[Error] Failed to save items.json: {e}")

    ## Loads items from file
    def load_items_old(self):
        if not os.path.exists(SAVE_FILE) or os.path.getsize(SAVE_FILE) == 0:
            self.items = []
            return
        try:
            with open(SAVE_FILE, 'r') as f:
              try:
                data = json.load(f)
              except json.JSONDecodeError:
                data = []
                self.items = [Item.from_dict(d) for d in data]
                self.items = [Item.from_dict(item) for item in data]
        except json.JSONDecodeError as e:
            print(f"Error loading items.json: {e}")
            messagebox.showerror("Load Error", "The items.json file is corrupted or invalid.")
            self.items = []

    ## Saves items to file ##
    def save_items_old(self):
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

        tk.Label(self.root, text="Enter Item Name:", font=APP_FONT).pack(pady=5)

        # Item Name Entry (auto‑pop OSK on focus)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)
        # bind focus‑in to launch OSK
        self.name_entry.bind(
            "<Button-1>",
            lambda e: OnScreenKeyboard(self.root, self.name_entry)
        )

        # — Expiration date picker (unchanged) —
        tk.Label(self.root, text="Select Expiration Date:", font=APP_FONT, justify="center").pack()
        self.date_picker = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.date_picker.pack(pady=5)

        # Barcode Entry (auto‑pop OSK on focus)
        label_code = tk.Label(self.root, text="Enter Barcode Number:", font=APP_FONT, justify="center")
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
            #imgtk = ImageTk.PhotoImage(image=img)
            self.imgtk = ImageTk.PhotoImage(image=img)
            #self.camera_label.imgtk = imgtk
            self.camera_label.config(image=self.imgtk)
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
        #if self.cpt.isOpened():
        if hasattr(self, "cpt") and self.cap.isOpened():
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
            self.barcode_entry.delete(0, tk.END)
            self.barcode_entry.insert(0, data)
            self.barcode_label.config(text=f"Detected: {data}")
            self.beep_and_flash()
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

def get_weather(city="Shreveport, US"):
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

weather_label = tk.Label(root, text="Loading weather...", font=APP_FONT)
weather_label.pack(pady=20)

class WeatherApp:
    #def __init__(self, root, backgroundImg, backImg, back_callback=None):
    def __init__(self, root, backImg, back_callback=None):
        self.root = root
        self.root.title("Weather Forecast")
        self.backImg = backImg
        self.back_callback = back_callback
	## Frame For Weather App Content ##
        self.frame = tk.Frame(self.root)
        #self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.frame.pack(fill="both", expand=True)
        self.frame.bind("<Configure>", lambda event: self.update_background_image())

        self.set_background()

	## Back Button Image ##
        self.backImg = ImageTk.PhotoImage(Image.open("pics/icons/back.png"))
        self.back_callback = back_callback

        self.city = CITY
        self.api_key = KEY_WEATHER
        #self.city = "Shreveport, US"
        #self.api_key = "f63847d7129eb9be9c7a464e1e5ef67b"  # Your OpenWeatherMap API key

        self.weather_ui()
        #self.update_weather()

    def set_background(self):
#    def set_background(self, path=None):
#        if path is None:
#            path = self.current_background or "pics/backgrounds/back.jpg"
        default_path = "pics/backgrounds/weather.jpg"
        background_path = default_path

        try:
            # Get current weather condition and icon code
            #condition, icon_code = self.get_current_weather_condition()
            #background_path = self.get_background_path_for_condition(condition, icon_code)
            condition, icon_code = self.get_current_weather_condition()
            background_path = self.get_background_path_for_condition(condition, icon_code)

            print(f"Detected weather condition: {condition}")
            print(f"Icon Code: {icon_code}")

            # Normalize condition and day/night
            is_night = icon_code.endswith("n")
            condition = condition.lower()

            # Mapping for day conditions
            condition_map = {
                "clear": "clear",
                "clouds": "cloudy",
                "rain": "rain",
                "drizzle": "rain",
                "thunderstorm": "stormy",
                "snow": "snowy",
                "mist": "foggy",
                "fog": "foggy",
                "haze": "foggy",
                "smoke": "foggy",
                "dust": "foggy",
                "sand": "foggy",
                "ash": "foggy",
                "squall": "stormy",
                "tornado": "stormy"
            }

            condition_key = condition_map.get(condition, icon_code, "weather")
            if is_night:
                # Apply your preferred naming pattern
                if condition_key == "cloudy":
                    condition_key = "night_cloudy"
                elif condition_key == "snowy":
                    condition_key = "night_snowy"
                else:
                    condition_key = f"night_{condition_key}"

            background_path = f"pics/backgrounds/{condition_key}.jpg"

            print(f"Using Background: {background_path}")

            # Load the image
            self.bg_image_original = Image.open(path)
            self.update_background_image()
            return

        except Exception as e:
            print(f"Error setting background image: {e}")
            print(f"Falling back to default background: {default_path}")
            self.bg_image_original = Image.open(default_path)
            self.update_background_image()

    def on_resize(self, event):
        if hasattr(self, "bg_image_original"):
            resized = self.bg_image_original.resize((event.width, event.height), Image.LANCZOS)
            self.backgroundImg = ImageTk.PhotoImage(resized)
            if hasattr(self, "bg_label"):
                self.bg_label.config(image=self.backgroundImg)
                self.bg_label.image = self.backgroundImg
                self.bg_label.lower()

    def update_background_image(self):
        if hasattr(self, 'bg_image_original'):
            width = self.root.winfo_width()
            height = self.root.winfo_height()

            resized_image = self.bg_image_original.resize((width, height), Image.LANCZOS)
            self.backgroundImg = ImageTk.PhotoImage(resized_image)

            if hasattr(self, 'bg_label'):
                self.bg_label.config(image=self.backgroundImg)
                self.bg_label.image = self.backgroundImg
                self.bg_label.lower()

    def update_background_image_old(self):
        if not hasattr(self, 'bg_image_original'):
            print("No original background image loaded.")
            return

        try:
            window_width = self.frame.winfo_width()
            window_height = self.frame.winfo_height()

            if window_width < 10 or window_height < 10:
                return  # Don't resize to invalid dimensions

            resized_image = self.bg_image_original.resize((window_width, window_height), Image.LANCZOS)
            self.backgroundImg = ImageTk.PhotoImage(resized_image)

            if not hasattr(self, 'bg_label') or not self.bg_label.winfo_exists():
                self.bg_label = tk.Label(self.frame)
                self.bg_label.place(relwidth=1, relheight=1)

            self.bg_label.configure(image=self.backgroundImg)
            self.bg_label.image = self.backgroundImg  # Keep reference

        except Exception as e:
            print("Error updating background image:", e)

    def get_background_path_for_condition(self, condition, icon_code):
        condition = condition.lower().replace(" ", "_")
        time_of_day = "night" if icon_code.endswith("n") else "day"

        ## Adjust condition naming
        condition = condition.replace("clouds", "cloudy")
        condition = condition.replace("snow", "snowy")

        base_path = "pics/backgrounds"
        preferred = f"{base_path}/{time_of_day}_{condition}.jpg"
        fallback = f"{base_path}/{time_of_day}_clear.jpg"
        default = f"{base_path}/weather.jpg"

        if os.path.exists(preferred):
            print(f"Using Background: {preferred}")
            return preferred
        elif os.path.exists(fallback):
            print(f"Falling back to: {fallback}")
            return fallback
        else:
            print(f"Falling back to default: {default}")
            return default

    def set_background_from_path(self, image_path):
        print(f"Loading background image from: {image_path}")
        try:
            self.bg_image_original = Image.open(image_path)
            self.update_background_image()
        except Exception as e:
            print(f"Failed to load background image: {image_path}\n{e}")
            self.bg_image_original = Image.open("pics/backgrounds/weather.jpg")
            self.update_background_image()

    def get_current_weather_condition(self):
        if not hasattr(self, 'city'):
            self.city = CITY
        if not hasattr(self, 'api_key'):
            self.api_key = KEY_WEATHER

        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.city}&appid={self.api_key}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        condition = data['weather'][0]['main']
        icon_code = data['weather'][0]['icon']
        return condition, icon_code

    def load_background_image(self, primary_path, condition=None, is_night=False):
        """
        Try to load the primary background image.
        If it fails, try the day_[condition].jpg fallback.
        If that fails, fall back to day_clear.jpg as final resort.
        """
        def try_load(path):
            try:
                print(f"Attempting to load background: {path}")
                return Image.open(path)
            except Exception as e:
                print(f"Failed to load image: {path}")
                print(e)
                return None

        # 1. Try the intended background image
        image = try_load(primary_path)

        # 2. If failed, try day_[condition].jpg
        if image is None and condition:
            fallback_day_path = f"pics/backgrounds/day_{condition.lower()}.jpg"
            image = try_load(fallback_day_path)

        # 3. If still failed, use day_clear.jpg
        if image is None:
            fallback_clear = "pics/backgrounds/day_clear.jpg"
            image = try_load(fallback_clear)

        # 4. Final fallback: gray image
        if image is None:
            print("All fallbacks failed. Using solid gray background.")
            image = Image.new("RGB", (800, 600), color="gray")

        # Store original image and update display
        self.bg_image_original = image
        self.update_background_image()

    def update_background_image(self):
        """
        Resize the loaded background image to the window size and apply it to the background label.
        """
        if not hasattr(self, 'bg_image_original'):
            print("No original background image loaded.")
            return

        try:
            window_width = self.frame.winfo_width()
            window_height = self.frame.winfo_height()

            # Fallback to default size if dimensions aren't ready yet
            if window_width < 10 or window_height < 10:
                window_width, window_height = 800, 600

            resized_image = self.bg_image_original.resize((window_width, window_height), Image.LANCZOS)
            self.backgroundImg = ImageTk.PhotoImage(resized_image)

            if hasattr(self, 'bg_label'):
                self.bg_label.config(image=self.backgroundImg)
                self.bg_label.image = self.backgroundImg
            else:
                self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
                self.bg_label.place(relwidth=1, relheight=1)
                self.bg_label.image = self.backgroundImg

        except Exception as e:
            print("Error updating background image:", e)


    def clear_screen(self):
        #for widget in self.root.winfo_children():
        for widget in self.frame.winfo_children():
            widget.destroy()

    def weather_ui(self):
        self.clear_screen()
#        self.set_background()

        # Load weather condition-based background BEFORE creating bg_label
        condition, icon_code = self.get_current_weather_condition()
        background_path = self.get_background_path_for_condition(condition, icon_code)
        self.set_background_from_path(background_path)

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
        #self.weather_label = tk.Label(self.root, font=APP_FONT)
        #self.weather_label = tk.Label(content_frame, font=APP_FONT, bg="white")
        self.weather_label = tk.Label(content_frame, font=APP_FONT)
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

            #text_label = tk.Label(day_frame, font=APP_FONT, bg="white")
            text_label = tk.Label(day_frame, font=APP_FONT)
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
        #self.back_btn.place(relx=0.5, rely=0.95, anchor="s")
        self.back_btn.place(relx=1.0, x=-10, y=10, anchor="ne")
        #self.back_btn.place(x=10, y=10, anchor="s")
        self.back_btn.image = self.backImg
        ToolTip(self.back_btn, "Click to Return to the Previous Screen")

        self.update_weather()

    def update_weather(self):
        try:
            if not hasattr(self, 'city'):
                  self.city = "Shreveport, US"
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
            print(f"Detected weather condition: {condition}")
            icon_code = current['weather'][0]['icon']
            icon_img = self.get_icon(icon_code)

            # Set background based on condition
            background_path = self.get_background_path_for_condition(condition, icon_code)
            self.set_background_from_path(background_path)

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
        self.detected = False  # Track detection
        self.last_data = ""
        self.entry_var = tk.StringVar()  # For autofill
        self.detect_label = tk.Label(self.frame, text="", font=("Helvetica", 16), bg="white", fg="green")
        self.detect_label.place(relx=0.5, rely=0.85, anchor="center")
        self.entry_field = tk.Entry(self.frame, textvariable=self.entry_var, font=("Helvetica", 14))
        self.entry_field.place(relx=0.5, rely=0.9, anchor="center")
        self.animation_label = tk.Label(self.frame, text="✓", font=("Helvetica", 50), fg="green", bg="white")
        self.animation_label.place(relx=0.5, rely=0.5, anchor="center")
        self.animation_label.lower()

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

        #self.video_label = tk.Label(self.frame, bg="black")
        #self.video_label.place(relx=0.5, rely=0.4, anchor="center")

        self.canvas = tk.Canvas(self.frame, width=640, height=480, bg="black", highlightthickness=0)
        self.canvas.place(relx=0.5, rely=0.4, anchor="center")

        self.back_btn = tk.Button(self.frame, image=self.backImg, command=self.back_callback)
        self.back_btn.place(relx=0.5, rely=0.95, anchor="s")

    def update_frame(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = self.draw_overlay_rectangle(frame)
                barcodes = decode(frame)
                if barcodes and not self.detected:
                    data = barcodes[0].data.decode("utf-8")
                    self.last_data = data
                    self.entry_var.set(data)
                    self.detect_label.config(text=f"Detected: {data}")
                    self.play_beep()
                    self.animate_check()
                    self.detected = True
                    #threading.Timer(2, self.reset_detection).start()
                    self.frame.after(2000, self.reset_detection)

                for barcode in barcodes:
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                #self.video_label.configure(image=imgtk)
                #self.video_label.image = imgtk
            
                # Clear previous canvas image if it exists
                if hasattr(self, 'canvas_img_id'):
                    self.canvas.delete(self.canvas_img_id)

                # Draw new frame image on canvas at top-left corner
                self.canvas_img_id = self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
                self.canvas.imgtk = imgtk

        self.frame.after(10, self.update_frame)

    def draw_overlay_rectangle(self, frame):
        h, w, _ = frame.shape
        rect_w, rect_h = int(w * 0.6), int(h * 0.2)
        start_x = w // 2 - rect_w // 2
        start_y = h // 2 - rect_h // 2
        end_x = start_x + rect_w
        end_y = start_y + rect_h
        color = (0, 255, 0)
        thickness = 2
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), color, thickness)
        return frame

    def reset_detection(self):
        self.detected = False
        self.detect_label.config(text="")
        self.animation_label.lower()

    def play_beep(self):
        # macOS alternative: os.system('say beep') or use `playsound` with a beep .mp3
        try:
            #winsound.Beep(1000, 200)
            #threading.Thread(target=lambda: playsound("audio/beep.wav")).start()
            #threading.Thread(target=lambda: os.system('say "beep"')).start()
            threading.Thread(target=lambda: os.system('say -v Bells "ding"')).start()
        except:
            pass

    def beep_and_flash(self):
        # Flash background
        original_color = self.video_label["bg"]
        def flash():
            #self.video_label["bg"] = "yellow"
            self.canvas["bg"] = "yellow"
            #self.root.after(150, lambda: self.video_label.config(bg=original_color))
            self.root.after(150, lambda: self.canvas.config(bg=original_color))
        flash()

        # Play sound in a thread to avoid freezing UI
        #threading.Thread(target=lambda: playsound("beep.wav")).start()

    def animate_check(self):
        self.animation_label.lift()
        self.frame.after(500, self.animation_label.lower)
        self.frame.after(10, self.update_frame)

    def set_background_image(self, image_path):
        if hasattr(self, "bg_label") and self.bg_label:
            self.bg_label.destroy()

        self.bg_image_original = Image.open(image_path)
        self.backgroundImg = ImageTk.PhotoImage(self.bg_image_original)

        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

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
        # Clear previous widgets if needed
        for widget in self.frame.winfo_children():
            widget.destroy()

        # Spotify info
        self.track_label = tk.Label(self.frame, text="Loading...", font=APP_FONT, bg="white")
        self.track_label.pack(pady=20)
        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        # --- Top bar frame for back button ---
        top_bar = tk.Frame(self.frame, bg="", height=50)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        back_btn = tk.Button(
            top_bar,
            image=self.backImg,
            command=self.back_callback,
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        back_btn.pack(side=tk.RIGHT, padx=15, pady=10)

        tk.Button(controls, text="Play", font=APP_FONT, command=self.play).pack(side=tk.LEFT, padx=10)
        tk.Button(controls, text="Pause", command=self.pause).pack(side=tk.LEFT, padx=10)
        tk.Button(controls, text="Next", command=self.next_track).pack(side=tk.LEFT, padx=10)
        #back_btn = tk.Button(self.frame, image=self.backImg, command=self.back_callback, bg="SystemButtonFace", borderwidth=0, highlightthickness=0)
        #back_btn.place(relx=0.95, rely=0.05, anchor="ne")

        # --- Canvas and scrollbar for horizontal tracks ---
        track_container = tk.Frame(self.frame, bg="")
        track_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(20, 10))  # Note extra top padding (20) to push it down

        canvas = tk.Canvas(track_container, height=220, bg="white", highlightthickness=0)
        canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

        for name, artist, image_url, link in tracks[:5]:  # show 5 tracks
            label = tk.Label(self.frame, text=f"{name} - {artist}", bg="white", font=APP_FONT)
            label.pack()
        scrollbar = tk.Scrollbar(track_container, orient=tk.HORIZONTAL, command=canvas.xview)
        scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.configure(xscrollcommand=scrollbar.set)

        scroll_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        # Bind scroll region update
        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas.find_withtag("all")[0], width=max(canvas.winfo_width(), scroll_frame.winfo_reqwidth()))

        scroll_frame.bind("<Configure>", update_scrollregion)
        canvas.bind('<Configure>', update_scrollregion)

        # Load and display your tracks horizontally here
        #tracks = self.fetch_top_tracks()  # Or fetch_playlist_tracks()
        playlist_id = random.choice(COOKING_PLAYLIST_IDS)
        tracks = self.fetch_playlist_tracks(playlist_id)

        for name, artist, image_url, link in tracks[:5]:
            card = tk.Frame(scroll_frame, bg="white", bd=1, relief="solid", padx=5, pady=5)
            card.pack(side=tk.LEFT, padx=10, pady=10)

            try:
                img_data = requests.get(image_url, timeout=5).content
                img = Image.open(BytesIO(img_data)).resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(card, image=photo, bg="white", cursor="hand2")
                img_label.image = photo  # keep reference
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
            except Exception as e:
                print("Image load failed:", e)
                tk.Label(card, text="[Image not loaded]", bg="white").pack()

            tk.Label(card, text=name, bg="white", font=APP_FONT, wraplength=100).pack()
            tk.Label(card, text=artist, bg="white", font=APP_FONT, wraplength=100).pack()

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
        # Create a canvas and horizontal scrollbar
        canvas = tk.Canvas(self.frame, bg="white", height=220)
        canvas.pack(fill=tk.X, padx=20, pady=(40, 10))

        h_scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=canvas.xview)
        h_scrollbar.pack(fill=tk.X)

        canvas.configure(xscrollcommand=h_scrollbar.set)

        # Create a frame inside the canvas
        inner_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        # Populate the inner frame with track cards horizontally
        for name, artist, image_url, link in tracks[:5]:
            card = tk.Frame(inner_frame, bg="white", bd=1, relief="solid", padx=5, pady=5)
            card.pack(side=tk.LEFT, padx=10, pady=10)

            try:
                img_data = requests.get(image_url, timeout=5).content
                img = Image.open(BytesIO(img_data)).resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(card, image=photo, bg="white", cursor="hand2")
                img_label.image = photo  # Keep reference
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
            except Exception as e:
                print("Image load failed:", e)
                tk.Label(card, text="[Image failed]", bg="white").pack()

            tk.Label(card, text=name, font=APP_FONT, bg="white", wraplength=100).pack()
            tk.Label(card, text=artist, font=APP_FONT, bg="white", wraplength=100).pack()

        # Update scroll region after populating
        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def display_tracks_vert(self, tracks):
        track_frame = tk.Frame(self.frame, bg="white")
        track_frame.pack(pady=10)

        for name, artist, image_url, link in tracks[:5]:
           track_card = tk.Frame(track_frame, bg="white")
           track_card.pack(side=tk.LEFT, padx=10)
           #def render():
           #     label = tk.Label(self.frame, text=f"{name} - {artist}", bg="white", font=APP_FONT)
           #     label.pack()

           try:
                    img_data = requests.get(image_url, timeout=5).content
                    img = Image.open(BytesIO(img_data)).resize((100, 100))
                    photo = ImageTk.PhotoImage(img)
                    #img_label = tk.Label(self.frame, image=photo, cursor="hand2", bg="white")
                    #img_label.image = photo
                    #img_label.pack()
                    #img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
           except Exception as e:
                    print("Image load failed:", e)
                    fallback = tk.Label(self.frame, text="[Image not loaded]", bg="white")
                    fallback.pack()

           if photo:
                    img_label = tk.Label(track_card, image=photo, cursor="hand2", bg="white")
                    img_label.image = photo  # Prevent garbage collection
                    img_label.pack()
                    img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))

           tk.Label(track_card, text=name, font=APP_FONT, bg="white").pack()
           tk.Label(track_card, text=artist, font=APP_FONT, bg="white").pack()

            #self.frame.after(0, render)

           self.display_youtube_videos()

    def display_tracks_horizontal(self, tracks):
        # Clear previous content
        for widget in self.frame.winfo_children():
             if widget != self.bg_label:
                 widget.destroy()

        if hasattr(self, 'tracks_container'):
             self.tracks_container.destroy()

        self.tracks_container = tk.Frame(self.frame, bg="")
        self.tracks_container.pack(fill=tk.X, padx=10, pady=10)

        canvas = tk.Canvas(self.tracks_container, bg="white", height=240)
        canvas.pack(fill=tk.X, padx=10, pady=10)
        #canvas.pack(padx=10, pady=10)

        # Canvas + Scrollbar setup
        #canvas = tk.Canvas(self.frame, bg="white", height=240)
        #canvas.pack(fill=tk.X, padx=10, pady=10)

        scrollbar = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, command=canvas.xview)
        scrollbar.pack(fill=tk.X)

        canvas.configure(xscrollcommand=scrollbar.set)

        # Frame inside canvas
        inner_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        # Populate cards horizontally
        for name, artist, image_url, link in tracks:
            card = tk.Frame(inner_frame, bg="white", bd=1, relief="solid", padx=5, pady=5)
            card.pack(side=tk.LEFT, padx=10, pady=10)

            photo = None
            try:
                img_data = requests.get(image_url, timeout=5).content
                img = Image.open(BytesIO(img_data)).resize((100, 100))
                photo = ImageTk.PhotoImage(img)
            except Exception as e:
                print("Image load failed:", e)

            if photo:
                img_label = tk.Label(card, image=photo, bg="white", cursor="hand2")
                img_label.image = photo
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))

            tk.Label(card, text=name, font=APP_FONT, bg="white", wraplength=100).pack()
            tk.Label(card, text=artist, font=APP_FONT, bg="white", wraplength=100).pack()

        # Ensure scrollable width is set
        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

## NPR ##
def play_npr_stream():
    pygame.mixer.init()
    pygame.mixer.music.load("https://npr-ice.streamguys1.com/live.mp3")
    pygame.mixer.music.play()

def stop_npr_stream():
    pygame.mixer.music.stop()

def open_in_app_browser(url):
    webview.create_window("YouTube Video", url, width=960, height=540)
    webview.start()

def make_click_callback(url):
    return lambda e: open_in_app_browser(url)

def show_youtube_in_app(url, app_root):
    app_root.withdraw()  # hide the main Tkinter window
    try:
        webview.create_window(
            title="Now Playing on YouTube",
            url=url,
            width=960,
            height=540,
            resizable=True,
            frameless=False
        )
        webview.start()
    finally:
        app_root.deiconify()

## Music Page ##
class MusicApp:
    def __init__(self, root, backgroundImg, backImg, back_callback, token):
        self.root = root
        self.backgroundImg = backgroundImg
        self.backImg = backImg
        self.back_callback = back_callback
        self.token = token
        self.nprImg = ImageTk.PhotoImage(Image.open("pics/icons/npr.png").resize((100, 100)))
        self.podImg = ImageTk.PhotoImage(Image.open("pics/icons/podcast.png").resize((100, 100)))
        self.bg_label_music = None
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

#        self.set_background()
        self.set_background_image("pics/backgrounds/music.jpg")
        self.create_music_screen()

#        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
#        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
#        self.bg_label.lower()

        self.npr_player = None
        self.npr_playing = False

        self.klpi_player = None
        self.klpi_playing = False

        self.create_ui()

    def set_background_new(self, path=None):
        try:
            if path is None:
                path = self.current_background or "pics/backgrounds/back.jpg"

            # Fix: If user picked a named theme like 'black', turn it into a real path
            if not os.path.exists(path) and not path.endswith(".jpg"):
                path = f"pics/backgrounds/{path}.jpg"

            if not os.path.exists(path):
                raise FileNotFoundError(f"Background image not found: {path}")

            self.bg_image_original = Image.open(path)
            self.current_background = path  # persist path

            # ... continue with bg_label logic ...
            # create bg_label, resize, bind etc.
        except Exception as e:
            print(f"Error loading background image: {e}")

    def set_background(self):
        self.bg_image_original = Image.open("pics/backgrounds/back.jpg")  # Or whichever image applies
        self.bg_label = tk.Label(self.frame)  # Assuming self.frame is your container
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        self.update_background_image()
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.update_background_image()

    def update_background_image(self):
        if not hasattr(self, 'bg_image_original') or not self.bg_image_original:
            return  # No image to use

        if not hasattr(self, 'bg_label') or not self.bg_label or not self.bg_label.winfo_exists():
            return  # bg_label was destroyed

        width = self.root.winfo_width()
        height = self.root.winfo_height()

        resized_image = self.bg_image_original.resize((width, height), Image.LANCZOS)
        self.backgroundImg = ImageTk.PhotoImage(resized_image)

        self.bg_label.config(image=self.backgroundImg)
        self.bg_label.image = self.backgroundImg

    def set_background_image(self, image_path):
        if hasattr(self, 'bg_label') and self.bg_label:
            self.bg_label.destroy()
            self.bg_label = None

        self.bg_image_original = Image.open(image_path)
        self.backgroundImg = ImageTk.PhotoImage(self.bg_image_original)

        self.bg_label = tk.Label(self.frame, image=self.backgroundImg)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.bg_label.lower()

    def create_music_screen(self):
        self.clear_screen()
        self.set_background_image("pics/backgrounds/music.jpg")

        # Remove home screen background if still visible
        if hasattr(self, "bg_label") and self.bg_label:
            self.bg_label.destroy()
            self.bg_label = None

        self.frame = tk.Frame(self.root, bg="white")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Custom music background
        music_bg_path = "pics/backgrounds/music.jpg"
        if not os.path.exists(music_bg_path):
            music_bg_path = "pics/backgrounds/day_clear.jpg"  # fallback

        try:
            image = Image.open(music_bg_path)
            self.bg_music_img_raw = image
            self.bg_music_img = ImageTk.PhotoImage(image)

            if self.bg_label_music:
                self.bg_label_music.destroy()

            self.bg_label_music = tk.Label(self.frame, image=self.bg_music_img)
            self.bg_label_music.place(relwidth=1, relheight=1)
            self.bg_label_music.lower()

            self.frame.bind("<Configure>", self._resize_music_bg)
        except Exception as e:
            print("Failed to load music background:", e)

    def _resize_music_bg(self, event):
        if not hasattr(self, "bg_music_img_raw") or not self.bg_music_img_raw:
            return

        resized = self.bg_music_img_raw.resize((event.width, event.height), Image.Resampling.LANCZOS)
        self.bg_music_img = ImageTk.PhotoImage(resized)

        if self.bg_label_music:
            self.bg_label_music.config(image=self.bg_music_img)

    def clear_screen(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def toggle_npr(self):
        if not self.npr_playing:
            self.play_npr()
            self.npr_playing = True
        else:
            self.stop_npr()
            self.npr_playing = False

    def toggle_klpi(self):
        #if not self.klpi_playing:
        if self.klpi_player and self.klpi_player.is_playing():
            self.klpi_player.stop()
            self.klpi_player = None
        else:
            try:
                #self.klpi_player = vlc.MediaPlayer("https://klpi.latech.edu/listen")
                self.klpi_player = vlc.MediaPlayer("https://138.47.83.50:8080/stream")
                self.klpi_player.play()
            except Exception as e:
                print(f"Error playing KLPI: {e}")

    def create_ui(self):
        #tk.Button(self.frame, image=self.backImg, command=self.back_callback).place(relx=0.05, rely=0.9)

        # --- Spotify Section ---
        self.track_label = tk.Label(self.frame, text="Loading Spotify info...", font=APP_FONT, bg="white")
        self.track_label.pack(pady=10)

        self.album_art_label = tk.Label(self.frame, bg="white")
        self.album_art_label.pack(pady=10)

        controls = tk.Frame(self.frame, bg="white")
        controls.pack(pady=10)

        tk.Button(controls, text="Play", font=APP_FONT, command=self.play_spotify).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Pause", font=APP_FONT, command=self.pause_spotify).pack(side=tk.LEFT, padx=5)
        tk.Button(controls, text="Next", font=APP_FONT, command=self.next_track).pack(side=tk.LEFT, padx=5)

        # NPR + Podcasts Side-by-Side
        npr_controls = tk.Frame(self.frame, bg="white")
        npr_controls.pack(pady=20)

        # NPR button (acts as play/pause)
        npr_btn = tk.Button(npr_controls, image=self.nprImg, command=self.toggle_npr, bd=0)
        npr_btn.pack(side=tk.LEFT, padx=10)

        #klpi_btn = tk.Button(parent_frame, image=klpiImg, command=self.toggle_klpi)
        klpi_btn = tk.Button(npr_controls, image=klpiImg, command=self.toggle_klpi)
        klpi_btn.pack(side="left", padx=10)

        # Podcast button next to NPR
        podcast_btn = tk.Button(
            npr_controls,
            image=self.podImg,
            command=self.open_apple_podcast,
            bd=0,
            highlightthickness=0
        )
        podcast_btn.pack(side=tk.LEFT, padx=10)

        # Icons side by side
#        icons_frame = tk.Frame(npr_controls, bg="white")
#        icons_frame.pack()

#        npr_btn = tk.Button(icons_frame, image=self.nprImg, command=self.play_npr, bd=0, highlightthickness=0)
#        npr_btn = tk.Button(npr_controls, image=self.nprImg, command=self.toggle_npr)
#        npr_btn.pack(side=tk.LEFT, padx=10)

#        podcast_btn = tk.Button(icons_frame, image=self.podImg, command=self.open_apple_podcast, bd=0, highlightthickness=0)
#        podcast_btn.pack(side=tk.LEFT, padx=10)

        # NPR Controls under NPR icon
#        npr_play_controls = tk.Frame(npr_controls, bg="white")
#        npr_play_controls.pack(pady=5)

#        tk.Button(npr_play_controls, text="Play NPR", command=self.play_npr).pack(side=tk.LEFT, padx=5)
#        tk.Button(npr_play_controls, text="Stop NPR", command=self.stop_npr).pack(side=tk.LEFT, padx=5)

        ## NPR Section ##
        #npr_controls = tk.Frame(self.frame, bg="white")
        #npr_controls.pack(pady=20)

#        tk.Label(npr_controls, image=self.nprImg, font=APP_FONT).pack()

#        tk.Button(npr_controls, text="Play NPR", command=self.play_npr).pack(side=tk.LEFT, padx=10)
#        tk.Button(npr_controls, text="Stop", command=self.stop_npr).pack(side=tk.LEFT, padx=10)

        ## Apple Podcasts Button ##
#        podcast_btn = tk.Button(
#            self.frame,
#            image=podImg,
#            font=APP_FONT,
#            command=self.open_apple_podcast,
#            bd=0,
#            highlightthickness=0
#        )
#        podcast_btn.pack(pady=5)

        #podcast_frame = tk.Frame(self.frame, bg="white")
        #podcast_frame.pack(pady=(5, 0), anchor="w")
        #podcast_btn = tk.Button(podcast_frame, image=podImg, font=APP_FONT, command=self.open_apple_podcast)
        #podcast_btn.pack(side=tk.LEFT, padx=10, pady=2)
        #podcast_btn = tk.Button(self.frame, image=self.podImg, font=APP_FONT,
        #podcast_btn.pack(pady=(2, 0))

        back_btn = tk.Button(self.frame, image=self.backImg, command=self.back_callback, bd=0, highlightthickness=0)
        back_btn.place(relx=0.98, rely=0.02, anchor="ne")
        back_btn.lift()

        ## Spotify Horizontal Scrollbar ##
        track_container = tk.Frame(self.frame, bg="white")
        track_container.pack(fill=tk.X, padx=10, pady=(0, 10))  # Reduced top padding

        track_canvas = tk.Canvas(track_container, height=180, bg="white", highlightthickness=0)
        track_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

        h_scrollbar = tk.Scrollbar(track_container, orient="horizontal", command=track_canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        track_canvas.configure(xscrollcommand=h_scrollbar.set)

        scroll_frame = tk.Frame(track_canvas, bg="white")
        track_window = track_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        self.display_youtube_videos()

        def update_scrollregion(event):
            track_canvas.configure(scrollregion=track_canvas.bbox("all"))
            track_canvas.itemconfig(track_window, width=max(track_canvas.winfo_width(), scroll_frame.winfo_reqwidth()))

        scroll_frame.bind("<Configure>", update_scrollregion)
        track_canvas.bind('<Configure>', update_scrollregion)

        # Load and display tracks horizontally
        tracks = self.fetch_playlist_tracks()
        for name, artist, image_url, link in tracks[:5]:
            card = tk.Frame(scroll_frame, bg="white", bd=1, relief=tk.RIDGE)
            card.pack(side=tk.LEFT, padx=10, pady=5)

            try:
                img_data = requests.get(image_url, timeout=5).content
                img = Image.open(BytesIO(img_data)).resize((100, 100))
                photo = ImageTk.PhotoImage(img)

                img_label = tk.Label(card, image=photo, bg="white", cursor="hand2")
                img_label.image = photo
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))

            except Exception as e:
                print("Image load failed:", e)
                tk.Label(card, text="[Image not loaded]", bg="white").pack()

            tk.Label(card, text=name, bg="white", wraplength=100, font=APP_FONT_BOLD).pack()
            tk.Label(card, text=artist, bg="white", wraplength=100, font=APP_FONT).pack()

        self.display_youtube_videos()

    def load_music_data(self):
        self.update_now_playing()  # fetch and update current song
        #tracks = self.fetch_playlist_tracks()  # fetch playlist
        tracks = self.fetch_top_tracks()
        self.display_tracks(tracks)  # safely update UI

    def display_tracks(self, tracks):
        # Container frame for horizontal scroller
        track_container = tk.Frame(self.frame, bg="white")
        track_container.pack(fill=tk.X, padx=20, pady=(60, 10))

        # Canvas + horizontal scrollbar
        canvas = tk.Canvas(track_container, bg="white", height=200, highlightthickness=0)
        canvas.pack(side=tk.TOP, fill=tk.X, expand=False)

        h_scrollbar = tk.Scrollbar(track_container, orient=tk.HORIZONTAL, command=canvas.xview)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.configure(xscrollcommand=h_scrollbar.set)

        # Inner frame for tracks
        inner_frame = tk.Frame(canvas, bg="white")
        canvas.create_window((0, 0), window=inner_frame, anchor='nw')

        # Add each track horizontally
        for name, artist, image_url, link in tracks[:5]:
            card = tk.Frame(inner_frame, bg="white", bd=1, relief="solid", padx=5, pady=5)
            card.pack(side=tk.LEFT, padx=10, pady=10)

            try:
                img_data = requests.get(image_url, timeout=5).content
                img = Image.open(BytesIO(img_data)).resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(card, image=photo, bg="white", cursor="hand2")
                img_label.image = photo
                img_label.pack()
                img_label.bind("<Button-1>", lambda e, url=link: webbrowser.open(url))
            except Exception as e:
                print("Image load failed:", e)
                tk.Label(card, text="[Image failed]", bg="white").pack()

            tk.Label(card, text=name, font=APP_FONT, bg="white", wraplength=100).pack()
            tk.Label(card, text=artist, font=APP_FONT, bg="white", wraplength=100).pack()

        inner_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Keep back button visible on top
        #back_btn = tk.Button(self.frame, image=self.backImg, command=self.back_callback)
        ##back_btn.place(x=20, y=20)
        #back_btn.place(relx=0.98, y=20, anchor="ne")
        #back_btn.lift()

    def display_tracks_vert(self, tracks):
        for name, artist, image_url, link in tracks[:5]:
            def render():
                label = tk.Label(self.frame, text=f"{name} - {artist}", bg="white", font=APP_FONT)
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
        COOKING_PLAYLIST_IDS = [
            "41f2E73ciOG7QTKYmdGR9H",  # Recipe songs
            "47Hj1ZIkQnyJInPIBjcw0B",  # Cooking Songs – Dinner at Home
            "2GmVYyQ4fYpuh0V9c2Cm6f",  # Bitchin In The Kitchen
            #"16a2whRq5tsJHORZvb8LIM",  # Cooking, Baking and Kitchen Fun – Songs for Kids
            #"0wZWyIjYFQh7Ex06F3WCut",  # Feeding Picky Eaters
        ]
        playlist_id = random.choice(COOKING_PLAYLIST_IDS)
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }

        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code != 200:
                print("Failed to fetch playlist:", resp.text)
                return []

            data = resp.json()
            items = data.get("items", [])
            if not items:
                print("Playlist is Empty:", data)

            tracks = []
            for item in items:
                track = item.get("track")
                if track:
                    name = track.get("name", "Unknown")
                    artists = track.get("artists", [])
                    artist = artists[0].get("name", "Unknown") if artists else "Unknown"

                    images = track.get("album", {}).get("images", [])
                    image_url = images[0]["url"] if images else ""

                    external_urls = track.get("external_urls", {})
                    external_url = external_urls.get("spotify", "")

                    tracks.append((name, artist, image_url, external_url))

            return tracks

        except Exception as e:
            print("Error fetching playlist:", e)
            return []

    def fetch_top_tracks(self):
        url = "https://api.spotify.com/v1/search"
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        params = {
            "q": "Cooking",  # can be changed to match podcast/music mood
            "type": "track",
            "limit": 5
        }

        try:
            resp = requests.get(url, headers=headers, params=params, timeout=5)
            if resp.status_code != 200:
                print("Failed to fetch search results:", resp.text)
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

        except Exception as e:
            print("Error fetching top tracks:", e)
            return []

    def open_music_web(self):
        #import webview
        #webview.create_window("Spotify Player", "https://open.spotify.com")
        #webview.start()

        self.clear_screen()

        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        back_btn = tk.Button(frame, image=self.backImg, command=self.create_home_screen)
        back_btn.pack(anchor="nw", padx=10, pady=10)

        html = """
        <h2>Spotify Web Preview</h2>
        <a href='https://open.spotify.com'>Open Spotify in Browser</a>
        """
        label = HTMLLabel(frame, html=html)
        label.pack(padx=20, pady=20)

    def open_apple_podcast(self):

        def launch_podcast():
            # Hide main app window
            self.root.withdraw()

            # Create and start webview window
            window = webview.create_window(
                "Apple Podcasts - Cooking",
                "https://podcasts.apple.com/us/genre/podcasts-arts-food/id1307",
                width=1024,
                height=600
            )
            webview.start()

            # Re-show main app window after closing
            self.root.deiconify()

        # Launch webview on main thread (required by pywebview)
        launch_podcast()

    def display_youtube_videos(self):
#        import requests
#        from urllib.parse import quote
#        import webbrowser

        # --- Horizontal Scrollable Canvas for YouTube ---
        yt_container = tk.Frame(self.frame, bg="white")
        yt_container.pack(fill=tk.X, padx=10, pady=10)

        yt_canvas = Canvas(yt_container, height=240, bg="white", highlightthickness=0)
        yt_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)

        yt_scrollbar = Scrollbar(yt_container, orient="horizontal", command=yt_canvas.xview)
        yt_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        yt_canvas.configure(xscrollcommand=yt_scrollbar.set)

        scroll_frame = tk.Frame(yt_canvas, bg="white")
        yt_window = yt_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        def update_scrollregion(event):
            yt_canvas.configure(scrollregion=yt_canvas.bbox("all"))
            yt_canvas.itemconfig(yt_window, width=max(yt_canvas.winfo_width(), scroll_frame.winfo_reqwidth()))

        scroll_frame.bind("<Configure>", update_scrollregion)
        yt_canvas.bind("<Configure>", update_scrollregion)

        videos = [
             {
                "title": "Gordon Ramsay's Ultimate Cookery Course",
                "url": "https://www.youtube.com/watch?v=5uXIPhxL5XA",
                "thumb": "https://img.youtube.com/vi/5uXIPhxL5XA/0.jpg"
             },
             {
                "title": "Binging with Babish: Ratatouille",
                "url": "https://www.youtube.com/watch?v=iCMGPRiDXQg",
                "thumb": "https://img.youtube.com/vi/iCMGPRiDXQg/0.jpg"
             },
             {
                "title": "Jamie Oliver's Food Tube",
                "url": "https://www.youtube.com/watch?v=J6Vb4T2LCiI",
                "thumb": "https://img.youtube.com/vi/J6Vb4T2LCiI/0.jpg"
             }
        ]

        for video in videos:
            card = tk.Frame(scroll_frame, bg="white", bd=1, relief=tk.RIDGE)
            card.pack(side=tk.LEFT, padx=10, pady=5)

            try:
                img_data = requests.get(video["thumb"], timeout=5).content
                img = Image.open(BytesIO(img_data)).resize((120, 90))
                photo = ImageTk.PhotoImage(img)

                img_label = tk.Label(card, image=photo, bg="white", cursor="hand2")
                img_label.image = photo
                img_label.pack()
                #img_label.bind("<Button-1>", lambda e, url=video["url"]: webbrowser.open(url))
                #img_label.bind("<Button-1>", lambda e, url=video["url"]: open_in_app_browser(url))
                #img_label.bind("<Button-1>", make_click_callback(video["url"]))
                #img_label.bind("<Button-1>", lambda e, url=video["url"]: show_youtube_in_app(url))
                img_label.bind("<Button-1>", lambda e, url=video["url"]: show_youtube_in_app(url, self.root))
            except Exception as e:
                print("Failed to load YouTube thumbnail:", e)
                tk.Label(card, text="[Image not loaded]", bg="white").pack()

            tk.Label(card, text=video["title"], bg="white", wraplength=120, font=APP_FONT).pack()

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
