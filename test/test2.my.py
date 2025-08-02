## Import Libraries ##
import tkinter as tk
from tkinter import simpledialog, Button, Frame, Label, PhotoImage, Toplevel
from datetime import datetime
from tkcalendar import DateEntry
import cv2
from PIL import Image, ImageTk
import os
import sys
import random

### Create Home Page ###
root = tk.Tk()
#root.attributes('-fullscreen', True)

### Background Image ###
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
img_back = Image.open("pics/back.jpg").resize((screen_width, screen_height), Image.LANCZOS)
backImg = ImageTk.PhotoImage(img_back)
background = Label(root, image=backImg)
background.place(x=0, y=0, relwidth=1, relheight=1)

### Button Images ###
img_wdt, img_hgt = 100, 100
img_light = ImageTk.PhotoImage(Image.open("pics/light.png").resize((img_wdt, img_hgt)))
img_home = ImageTk.PhotoImage(Image.open("pics/home.png").resize((img_wdt, img_hgt)))
img_item = ImageTk.PhotoImage(Image.open("pics/item.png").resize((img_wdt, img_hgt)))
img_cam = ImageTk.PhotoImage(Image.open("pics/cam.jpg").resize((img_wdt, img_hgt)))
img_scan = ImageTk.PhotoImage(Image.open("pics/scan.jpg").resize((img_wdt, img_hgt)))
img_view = ImageTk.PhotoImage(Image.open("pics/view.png").resize((img_wdt, img_hgt)))

### Calendar Hidden ###
cal = DateEntry(root, date_pattern="yyyy-mm-dd")
cal.place_forget()

### Light/Dark Toggle ###
switch_value = True

def toggle():
    global switch_value
    root.config(background="#26242f" if switch_value else "white")
    switch_value = not switch_value

### Items and Classes ###
items = []

class Item:
    def __init__(self, name, expiration_date):
        self.name = name
        self.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")

    def days_until_expired(self):
        return (self.expiration_date - datetime.now()).days + 1

    def get_color(self):
        days = self.days_until_expired() - 1
        gradient_colors = ["#FF0000", "#FF1A00", "#FF3300", "#FF4D00", "#FF6600", "#FF8000",
                           "#FF9900", "#FFB200", "#FFCC00", "#FFE500", "#E5FF00", "#CCFF00",
                           "#99FF00", "#66FF00", "#33FF00"]
        if days < 0:
            return gradient_colors[0]
        elif days >= len(gradient_colors):
            return gradient_colors[-1]
        else:
            return gradient_colors[days]

def check_dates(days):
    return abs(days)

### Item List View (Hidden Initially) ###
list_frame = tk.Frame(root)
list_canvas = tk.Canvas(list_frame, bg="#26242f")
list_items_frame = tk.Frame(list_canvas, bg="#26242f")
scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=list_canvas.yview)

list_canvas.create_window((0, 0), window=list_items_frame, anchor="nw")
list_canvas.configure(yscrollcommand=scrollbar.set)

list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

def refresh_list():
    list_items_frame.update()
    for widget in list_items_frame.winfo_children():
        widget.destroy()
    for item in items:
        color = item.get_color()
        days = item.days_until_expired()
        text = f"{item.name} - Expires in {check_dates(days)} days" if days >= 0 else f"{item.name} - Expired {check_dates(days)} days ago"
        tk.Label(list_items_frame, text=text, bg=color, font=("Arial", 16)).pack(fill=tk.X, pady=5, padx=10)

### Add Item ###
def add_item():
    name = simpledialog.askstring("Add Item", "Enter item name:")
    if not name:
        return
    expiration_date = cal.get()
    try:
        item = Item(name, expiration_date)
        items.append(item)
        with open('items.txt', 'w') as f:
            for i in items:
                f.write(f"{i.name},{i.expiration_date.strftime('%Y-%m-%d')}\n")
        refresh_list()
        list_frame.place(relx=0.5, rely=0.6, anchor="center", relwidth=0.8, relheight=0.3)
    except ValueError:
        tk.messagebox.showerror("Error", "Invalid date format")

### Camera ###
cpt = cv2.VideoCapture(0)
cpt.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cam_widget = tk.Label(root, background="black")
cam_widget.place_forget()

def open_camera():
    cam_widget.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
    def update():
        _, frame = cpt.read()
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(opencv_image)
        photo = ImageTk.PhotoImage(image=img)
        cam_widget.config(image=photo)
        cam_widget.image = photo
        root.after(10, update)
    update()

### Dummy Barcode ###
def show_barcode():
    top = Toplevel(root)
    top.title("Barcode")
    img = Image.open("pics/barcode.png").resize((300, 100), Image.LANCZOS)
    img_tk = ImageTk.PhotoImage(img)
    Label(top, image=img_tk).pack()
    top.mainloop()

### Button Layout ###
btn_frame = Frame(root, bg="white")
btn_frame.place(relx=0.5, rely=0.4, anchor="center")

buttons = [
    (img_item, add_item),
    (img_light, toggle),
    (img_home, lambda: list_frame.place_forget()),
    (img_cam, open_camera),
    (img_scan, show_barcode),
    (img_view, lambda: None)
]

for i, (img, cmd) in enumerate(buttons):
    btn = Button(btn_frame, image=img, command=cmd, bg="white", activebackground="#ccc", bd=2)
    btn.grid(row=i//3, column=i%3, padx=20, pady=20, ipadx=10, ipady=10)

root.mainloop()
