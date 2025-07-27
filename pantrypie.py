import tkinter as tk
from tkinter import simpledialog, messagebox, Button, Label, StringVar, OptionMenu
from datetime import datetime
from tkcalendar import Calendar, DateEntry
import time
from time import strftime
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import matplotlib.pyplot as plt
import os
import sys
import json
import random

## Create Root ##
root = tk.Tk()
root.geometry("1024x600")
#root.geometry("1920x1080")
#root.title("Expiration Tracker")
root.title("Pantry Server")

## Variables ##
SAVE_FILE = "items.json"

### Import and Resize Button Images ###
## Button Size ##
img_wdt = 50
img_hgt = 50
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
## Save Image ##
img_save = Image.open("pics/save.jpg")
img_save = img_save.resize((img_wdt, img_hgt), Image.LANCZOS)
saveImg = ImageTk.PhotoImage(img_save)
## Scan Image ##
img_scan = Image.open("pics/scan.jpg")
img_scan = img_scan.resize((img_wdt, img_hgt), Image.LANCZOS)
scanImg = ImageTk.PhotoImage(img_scan)
## View Image ##
img_view = Image.open("pics/view.png")
img_view = img_view.resize((img_wdt, img_hgt), Image.LANCZOS)
viewImg = ImageTk.PhotoImage(img_view)

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

# ------- Main Application Class -------
class ExpirationApp:
    def __init__(self, root):
        self.root = root
        self.items = []  # List to hold all items
        self.barcode = barcode = None
        self.current_view = 'home'
        self.dark_mode = False  # Track dark mode state
        self.sort_option = StringVar()
        self.sort_option.set("Sort By")
        self.backgroundImg = ImageTk.PhotoImage(Image.open("pics/back.jpg").resize((1024, 600), Image.LANCZOS))
        self.card_backgroundImg = ImageTk.PhotoImage(Image.open("pics/back_pastel.jpg").resize((1024, 600), Image.LANCZOS))
        self.list_backgroundImg = ImageTk.PhotoImage(Image.open("pics/back_toon.jpg").resize((1024, 600), Image.LANCZOS))
        self.bg_color = "#f0f0f0"
        self.load_items()
        self.init_camera()
        self.create_tracker_screen()

    ## Create Background ##
    def set_background(self):
        background = tk.Label(self.root, image=self.backgroundImg)
        background.place(x=0, y=0, relwidth=1, relheight=1)
        background.lower()

    ## Create Home Screen ##
    def create_tracker_screen(self, item=None):
        self.clear_screen()
        self.set_background()

	    ## Background Greeting ##
        # Clock at the top
        self.clock_label = tk.Label(self.root, font=('calibri', 30, 'bold'), background='orange', foreground='yellow')
        self.clock_label.pack(pady=10)

        def update_clock():
            string = strftime("%A, %B %d %Y %H:%M:%S")
            self.clock_label.config(text=string)
            self.root.after(1000, update_clock)

        update_clock()

        # Enlarged calendar
        self.cal = Calendar(self.root, selectmode='day', date_pattern="yyyy-mm-dd")
        self.cal.pack(pady=20, ipady=10, ipadx=10)

        # Buttons side by side
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)

        track_btn = tk.Button(button_frame, image=viewImg, width=100, height=100, command=lambda: self.create_tracker_ui(item))
        track_btn.pack(side=tk.LEFT, padx=20)

        dark_mode_btn = tk.Button(button_frame, image=lightImg, width=100, height=100, command=self.toggle_dark_mode)
        dark_mode_btn.pack(side=tk.LEFT, padx=20)


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
			#text="Add Item",
			image=addImg,
			#command=lambda: self.add_item_popup)
			command=self.add_item_popup)
        add_btn.pack(pady=5)

	## Open Camera ##
        add_btn = tk.Button(self.root,
			#text="Add Item",
			image=camImg,
			#command=lambda: self.add_item_popup)
			command=self.update_camera)
        add_btn.pack(pady=5)

	## Show List View ##
        list_view_btn = tk.Button(self.root,
				#text="List View",
				image=listImg,
				#command=lambda: self.create_list_view)
				command=self.create_list_view)
        list_view_btn.pack(pady=5)

	## Show Card View ##
        card_view_btn = tk.Button(self.root,
				#text="Card View",
				image=cardImg,
				#command=lambda: self.create_card_view)
				command=self.create_card_view)
        card_view_btn.pack(pady=5)

	## Mode ##
        dark_mode_btn = tk.Button(self.root,
				#text="Toggle Dark Mode",
				image=lightImg,
				#command=lambda: self.toggle_dark_mode)
				command=self.toggle_dark_mode)
        dark_mode_btn.pack(pady=10)

	## Show Back ##
        tk.Button(self.root,
		image=backImg,
		command=lambda: self.create_tracker_screen(None)).pack(pady=10)

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
        canvas = tk.Canvas(self.root, height=450, bg="SystemButtonFace", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="SystemButtonFace")


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

        tk.Button(self.root, image=backImg, command=self.create_tracker_screen).pack(pady=10)
    
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
        canvas = tk.Canvas(self.root, height=450, bg="SystemButtonFace", highlightthickness=0, bd=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="SystemButtonFace")


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

        tk.Button(self.root, image=backImg, command=self.create_tracker_screen).pack(pady=10)

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
				#text="Open Scanner",
				image=camImg,
				#command=lambda: self.show_camera)
				command=self.show_camera)
        scanner_btn.pack(pady=5)

        barcode_btn = tk.Button(self.root,
				#text="Detect Barcode",
				image=scanImg,
				#command=lambda: self.detect_barcode("codes/barcode.png"))
				command=self.detect_barcode("codes/barcode.png"))
        barcode_btn.pack(pady=5)

        manual_btn = tk.Button(self.root, text="Enter Barcode", command=self.barcode_entry)
        manual_btn.pack(pady=10)

        # Back to card view
        back_btn = tk.Button(self.root,
			#text="Back",
			image=cardImg,
			#command=lambda: self.create_card_view)
			command=self.create_card_view)
        back_btn.pack(pady=10)


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

        tk.Label(self.root, text="Add New Item", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.root, text="Item Name:").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)

        tk.Label(self.root, text="Expiration Date:").pack()
        self.date_picker = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.date_picker.pack(pady=5)

        tk.Label(self.root, text="Barcode Number (Auto Fills Name):").pack()
        self.barcode_entry = tk.Entry(self.root)
        self.barcode_entry.pack(pady=5)

        # Allow barcode to pre-fill name
        #barcode_btn = tk.Button(self.root, text="Enter Barcode to Autofill Name", command=self.barcode_entry())
        #barcode_btn = tk.Button(self.root, text="Enter Barcode to Autofill Name", command=self.barcode_entry)
        #barcode_btn.pack(pady=10)

        tk.Button(self.root,
		#text="Scan",
		image=scanImg,
		#command=lambda: self.save_new_item).pack(pady=5)
		command=self.detect_barcode("codes/barcode.png")).pack(pady=5)
        tk.Button(self.root,
		#text="Save",
		image=saveImg,
		#command=lambda: self.save_new_item).pack(pady=5)
		command=self.save_new_item).pack(pady=5)
        tk.Button(self.root,
		#text="Save",
		image=lightImg,
		#command=lambda: self.save_new_item).pack(pady=5)
		command=self.toggle_dark_mode).pack(pady=5)
        tk.Button(self.root,
		#text="Back",
		image=backImg,
		command=lambda: self.create_tracker_ui(None)).pack(pady=5)
		#command=self.create_tracker_ui(None)).pack(pady=5)

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
        self.cpt = cv2.VideoCapture(0)
        self.cpt.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera_label = tk.Label(self.root)

    def show_camera(self):
        self.clear_screen()
        self.set_background()
        self.camera_label = tk.Label(self.root)
        self.camera_label.pack(pady=20)
        self.update_camera()
        tk.Button(self.root, text="Back", command=self.create_tracker_screen).pack(pady=10)

    def open_camera(self):
        # Show live feed from camera
        _, frame = self.cpt.read()
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        captured_image = Image.fromarray(opencv_image)
        photo_image = ImageTk.PhotoImage(image=captured_image)

#        self.label_widget.photo_image = photo_image
#        self.label_widget.configure(image=photo_image)
#        self.label_widget.pack()
        self.camera_label.photo_image = photo_image
        self.camera_label.configure(image=photo_image)
        self.camera_label.pack()

        self.root.after(10, self.open_camera)

    def update_camera(self):
      if not hasattr(self, "camera_label") or not self.camera_label.winfo_exists():
        return

      if not self.camera_label.winfo_exists():
        return

      if self.cpt.isOpened():
        ret, frame = self.cpt.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.config(image=imgtk)
      self.camera_loop_id = self.root.after(10, self.update_camera)

    def stop_camera(self):
        self.root.after_cancel(self.camera_loop_id)

    def detect_barcode(self, image_path):
        if not os.path.exists(image_path):
                print("Barcode Image Not Found.")
                return

        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)

        if not barcodes:
            print("No Barcode Found.")
            return

        for barcode in barcodes:
            data = barcode.data.decode("utf-8")
            print("Detected Barcode:", data)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imshow(rgb)
        plt.axis('off')
        plt.show()

if __name__ == "__main__":
#    root = tk.Tk()
#    root.geometry("1024x600")
#    root.title("Expiration Tracker")
    app = ExpirationApp(root)
    root.mainloop()
