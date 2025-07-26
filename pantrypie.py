import tkinter as tk
from tkinter import simpledialog, messagebox, Button, Label, StringVar, OptionMenu
from datetime import datetime
from tkcalendar import DateEntry
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import matplotlib.pyplot as plt
import os
import sys
import json
import random

SAVE_FILE = "items.json"
######################## ------- Item Model -------################################
class Item:
    def __init__(self, name, expiration_date):
        # Store name and parse expiration date
        self.name = name
        self.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")

    def to_dict(self):
        return {"name": self.name, "expiration_date": self.expiration_date.strftime("%Y-%m-%d")}

    @staticmethod
    def from_dict(data):
        return Item(data['name'], data['expiration_date'])

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
        self.current_view = 'home'
        self.dark_mode = False  # Track dark mode state
        self.sort_option = StringVar()
        self.sort_option.set("Sort By")
        self.load_items()
        self.init_camera()
        self.create_tracker_screen()
    # home screen

    def create_tracker_screen(self, item=None):
        self.clear_screen()

        # App Title
        label = tk.Label(self.root, text="Welcome to Expiration Tracker", font=("Arial", 20))
        label.pack(pady=20)

        # Calendar Picker
        self.cal = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.cal.pack(pady=10)

        track_btn = tk.Button(self.root, text="Go to Tracker", command=lambda: self.create_tracker_ui(item))
        track_btn.pack(pady=10)

        dark_mode_btn = tk.Button(self.root, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        dark_mode_btn.pack(pady=10)

    def create_tracker_ui(self, item):
        self.clear_screen()

        add_btn = tk.Button(self.root, text="Add Item", command=self.add_item_popup)
        add_btn.pack(pady=5)

        list_view_btn = tk.Button(self.root, text="List View", command=self.create_list_view)
        list_view_btn.pack(pady=5)

        card_view_btn = tk.Button(self.root, text="Card View", command=self.create_card_view)
        card_view_btn.pack(pady=5)

    def create_card_view(self):
        self.clear_screen()
        
        # sets view for other functions as card
        self.current_view = "card" 

        # Sort Menu
        sort_menu = OptionMenu(self.root, self.sort_option, "Expiration (Soonest)", "Expiration (Latest)", "Name (A-Z)", "Name (Z-A)", command=self.sort_items)
        sort_menu.pack(pady=10)

        self.card_frame = tk.Frame(self.root)
        self.card_frame.pack(fill=tk.BOTH, expand=True)

        self.cards_container = tk.Frame(self.card_frame)
        self.cards_container.pack()

        row = col = 0
        for item in self.items:
            color = item.get_color()
            days = item.days_until_expired()
            text = f"{item.name} - Expires in {check_dates(days)} days" if days >= 0 else f"{item.name} - Expired {check_dates(days)} days ago"
            c_btn = tk.Button(
                self.cards_container, text=text, bg=color, fg="black", font=("Arial", 16), wraplength=150,
                width=15, height=6,  
                command=lambda i=item: self.show_detail_view(i)
            )
            c_btn.grid(row=row, column=col, padx=10, pady=10)
            col += 1
            if col == 3:
                col = 0
                row += 1

        back_btn = tk.Button(self.root, text="Back", command=lambda: self.create_tracker_ui(None))
        back_btn.pack(pady=10)


    def create_list_view(self):
        self.clear_screen()

        # sets view for other functions as list
        self.current_view = "list" 

        # Sort menu
        sort_menu = OptionMenu(self.root, self.sort_option, "Expiration (Soonest)", "Expiration (Latest)", "Name (A-Z)", "Name (Z-A)", command=self.sort_items)
        sort_menu.pack(pady=5)

        for item in self.items:
            frame = tk.Frame(self.root)
            frame.pack(fill=tk.X, pady=2)

            color = item.get_color()
            days = item.days_until_expired()
            text = f"{item.name} - Expires in {check_dates(days)} days" if days >= 0 else f"{item.name} - Expired {check_dates(days)} days ago"
            tk.Label(frame, text=text, bg=color, fg="black", font=("Arial", 14)).pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Button(frame, text="Delete", command=lambda i=item: self.delete_item(i)).pack(side=tk.RIGHT, padx=5)

        tk.Button(self.root, text="Back", command=lambda: self.create_tracker_ui(None)).pack(pady=10)

    def refresh_views(self):
        if self.current_view == "card":
            self.create_card_view()
        elif self.current_view == "list":
            self.create_list_view()

    def show_detail_view(self, item):
        self.clear_screen()
        days = item.days_until_expired()

        # Show item details
        detail_text = (
            f"Item: {item.name}\n"
            f"Expiration: {item.expiration_date.strftime('%Y-%m-%d')}\n"
            f"Days Left: {check_dates(days) if days > 0 else 0}"
        )

        label = tk.Label(self.root, text=detail_text, font=("Arial", 20), justify="left")
        label.pack(pady=30)

        # Scanner and barcode buttons (only shown on item click)
        scanner_btn = tk.Button(self.root, text="Open Scanner", command=self.show_camera)
        scanner_btn.pack(pady=5)

        barcode_btn = tk.Button(self.root, text="Detect Barcode", command=lambda: self.detect_barcode("barcode.png"))
        barcode_btn.pack(pady=5)

        manual_btn = tk.Button(self.root, text="Enter Barcode", command=lambda: self.manual_barcode_entry)
        manual_btn.pack(pady=10)

        # Back to card view
        back_btn = tk.Button(self.root, text="Back", command=self.create_card_view)
        back_btn.pack(pady=10)

    def manual_barcode_entry(self, item=None):
        # Ask user to type in barcode manually
        barcode = simpledialog.askstring("Barcode Entry", "Enter barcode number:")
        if not barcode:
            return
        self.fetch_open_food_facts(barcode)

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

            else:
                messagebox.showerror("Error", "Product not found in Open Food Facts.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")

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

        tk.Label(self.root, text="Add New Item", font=("Arial", 20)).pack(pady=20)

        tk.Label(self.root, text="Item Name:").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)

        tk.Label(self.root, text="Expiration Date:").pack()
        self.date_picker = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.date_picker.pack(pady=5)

        # Allow barcode to pre-fill name
        barcode_btn = tk.Button(self.root, text="Enter Barcode to Autofill Name", command=self.manual_barcode_entry())
        barcode_btn.pack(pady=10)

        tk.Button(self.root, text="Save", command=self.save_new_item).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.create_tracker_ui).pack(pady=5)

    def save_new_item(self):
        name = self.name_entry.get()
        date = self.date_picker.get()
        if not name:
            messagebox.showerror("Error", "Item name required")
            return
        try:
            item = Item(name, date)
            self.items.append(item)
            self.save_items()
            self.create_tracker_ui(item)
        except:
            messagebox.showerror("Error", "Invalid date")

    def save_items(self):
        with open(SAVE_FILE, 'w') as f:
            json.dump([item.to_dict() for item in self.items], f)

    def load_items(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
                self.items = [Item.from_dict(d) for d in data]

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def init_camera(self):
        self.cpt = cv2.VideoCapture(0)
        self.cpt.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera_label = tk.Label(self.root)

    def show_camera(self):
        self.clear_screen()
        self.camera_label.pack()
        self.update_camera()
        tk.Button(self.root, text="Back", command=self.create_tracker_screen).pack(pady=10)
    
    def open_camera(self):
        # Show live feed from camera
        _, frame = self.cpt.read()
        opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        captured_image = Image.fromarray(opencv_image)
        photo_image = ImageTk.PhotoImage(image=captured_image)

        self.label_widget.photo_image = photo_image
        self.label_widget.configure(image=photo_image)
        self.label_widget.pack()

        self.root.after(10, self.open_camera)

    def update_camera(self):
        ret, frame = self.cpt.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.config(image=imgtk)
        self.root.after(10, self.update_camera)

    def detect_barcode(self, image_path):
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)

        for barcode in barcodes:
            data = barcode.data.decode("utf-8")
            print("Detected Barcode:", data)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imshow(rgb)
        plt.axis('off')
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x600")
    root.title("Expiration Tracker")
    app = ExpirationApp(root)
    root.mainloop()