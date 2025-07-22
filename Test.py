import tkinter as tk
from tkinter import simpledialog, messagebox, Button, Label
from datetime import datetime
from tkcalendar import DateEntry
import cv2
from PIL import Image, ImageTk
from pyzbar.pyzbar import decode
import matplotlib.pyplot as plt
import os
import sys

# ------- Item Model -------
class Item:
    def __init__(self, name, expiration_date):
        # Store name and parse expiration date
        self.name = name
        self.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")

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
        self.init_camera()
        self.create_home_screen()

    def create_home_screen(self):
        self.clear_screen()

        # App Title
        label = tk.Label(self.root, text="Welcome to Expiration Tracker", font=("Arial", 20))
        label.pack(pady=20)

        # Calendar Picker
        self.cal = DateEntry(self.root, date_pattern="yyyy-mm-dd")
        self.cal.pack(pady=10)

        # Navigation Buttons
        home_btn = tk.Button(self.root, text="Go to Tracker", command=self.create_tracker_ui)
        home_btn.pack(pady=10)

        cam_btn = tk.Button(self.root, text="Open Scanner", command=self.open_camera)
        cam_btn.pack(pady=10)

        barcode_btn = tk.Button(self.root, text="Detect Barcode", command=lambda: self.detect_barcode("barcode.png"))
        barcode_btn.pack(pady=10)

        dark_mode_btn = tk.Button(self.root, text="Toggle Dark Mode", command=self.toggle_dark_mode)
        dark_mode_btn.pack(pady=10)

    def create_tracker_ui(self):
        self.clear_screen()

        # Add Item Button
        add_btn = tk.Button(self.root, text="Add Item", command=self.add_item_popup)
        add_btn.pack(pady=10)

        # Frame to contain cards
        self.card_frame = tk.Frame(self.root)
        self.card_frame.pack(fill=tk.BOTH, expand=True)

        self.cards_container = tk.Frame(self.card_frame)
        self.cards_container.pack()

        self.refresh_views()

    def refresh_views(self):
        # Clear old cards
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        row = 0
        col = 0
        for item in self.items:
            color = item.get_color()
            days = item.days_until_expired()
            text = f"{item.name} - Expires in {check_dates(days)} days" if days >= 0 else f"{item.name} - Expired {check_dates(days)} days ago"

            # Create item card as a button
            c_btn = tk.Button(
                self.cards_container, text=text, bg=color, fg="black", font=("Arial", 18), wraplength=150,
                command=lambda i=item: self.show_detail_view(i)
            )
            c_btn.grid(row=row, column=col, padx=20, pady=20, ipadx=20, ipady=20)

            col += 1
            if col >= 3:
                col = 0
                row += 1

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

        # Back and Scan Buttons
        back_btn = tk.Button(self.root, text="Back", font=("Arial", 16), command=self.create_tracker_ui)
        back_btn.pack(pady=10)

        scan_btn = tk.Button(self.root, text="Scan Barcode", command=self.open_camera)
        scan_btn.pack(pady=10)

        manual_btn = tk.Button(self.root, text="Enter Barcode", command=lambda: self.manual_barcode_entry(item))
        manual_btn.pack(pady=10)

        edit_btn = tk.Button(self.root, text="Edit Item", command=lambda: self.edit_item(item))
        edit_btn.pack(pady=10)

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

    def toggle_dark_mode(self):
        # Switch background and foreground colors
        self.dark_mode = not self.dark_mode
        bg = "#2E2E2E" if self.dark_mode else "white"
        fg = "white" if self.dark_mode else "black"
        self.root.configure(bg=bg)
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

    def manual_barcode_entry(self, item):
        # Ask user to type in barcode manually
        barcode = simpledialog.askstring("Barcode Entry", "Enter barcode number:")
        if not barcode:
            return
        self.fetch_open_food_facts(barcode, item)

    def fetch_open_food_facts(self, barcode, item):
        # Fetch product data from Open Food Facts API
        import requests

        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
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

                self.show_nutrition_info(nutrition_info)

                if not item.name:
                    item.name = nutrition_info["Product Name"]
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

    def add_item_popup(self):
        # UI to add a new item
        self.clear_screen()

        title = tk.Label(self.root, text="Add New Item", font=("Arial", 20))
        title.pack(pady=20)

        name_label = tk.Label(self.root, text="Item Name:", font=("Arial", 14))
        name_label.pack()
        self.name_entry = tk.Entry(self.root, font=("Arial", 14))
        self.name_entry.pack(pady=5)

        date_label = tk.Label(self.root, text="Expiration Date:", font=("Arial", 14))
        date_label.pack()
        self.date_picker = DateEntry(self.root, date_pattern="yyyy-mm-dd", font=("Arial", 14))
        self.date_picker.pack(pady=5)

        save_button = tk.Button(self.root, text="Save Item", font=("Arial", 14), command=self.save_new_item)
        save_button.pack(pady=10)

        back_button = tk.Button(self.root, text="Back", font=("Arial", 14), command=self.create_tracker_ui)
        back_button.pack(pady=5)

    def save_new_item(self):
        # Save item after filling form
        name = self.name_entry.get().strip()
        expiration_date = self.date_picker.get()

        if not name:
            messagebox.showerror("Error", "Item name cannot be empty.")
            return

        try:
            item = Item(name, expiration_date)
            self.items.append(item)
            self.create_tracker_ui()
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD.")

    def clear_screen(self):
        # Remove all widgets from root
        for widget in self.root.winfo_children():
            widget.destroy()

    def init_camera(self):
        # Initialize camera capture
        self.cpt = cv2.VideoCapture(0)
        self.cpt.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.label_widget = Label(self.root)

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

    def detect_barcode(self, image_path):
        # Detect barcode from image
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        barcodes = decode(gray)

        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            barcode_type = barcode.type

            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

            cv2.putText(image, f"{barcode_data} ({barcode_type})", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            print(f"Detected Barcode: {barcode_data} (Type: {barcode_type})")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        plt.imshow(image_rgb)
        plt.axis('off')
        plt.show()

# ------- Run App -------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Expiration Tracker")
    root.geometry("1024x600")
    app = ExpirationApp(root)
    root.mainloop()
