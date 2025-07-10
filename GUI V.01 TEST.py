import tkinter as tk
from tkinter import simpledialog
from datetime import datetime, timedelta

# Class to represent each item (food/drink) with name and expiration date
class Item:
    def __init__(self, name, expiration_date):
        self.name = name
        self.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")

    # Calculate how many days until the item expires
    def days_until_expired(self):
        return (self.expiration_date - datetime.now()).days

    # Return a color based on how close the item is to expiring
    def get_color(self):
        days = self.days_until_expired()
        gradient_colors = [
            "#FF0000",  # 1
            "#FF1A00",  # 2
            "#FF3300",  # 3
            "#FF4D00",  # 4
            "#FF6600",  # 5
            "#FF8000",  # 6
            "#FF9900",  # 7
            "#FFB200",  # 8
            "#FFCC00",  # 9
            "#FFE500",  # 10
            "#E5FF00",  # 11
            "#CCFF00",  # 12
            "#99FF00",  # 13
            "#66FF00",  # 14
            "#33FF00",  # 15
        ]
        if days < 0:
            return gradient_colors[0]
        elif days >= len(gradient_colors):
            return gradient_colors[-1]
        else:
            return gradient_colors[days]

import tkinter as tk
from datetime import datetime
from tkinter import simpledialog

# -------- Item Class --------
class Item:
    def __init__(self, name, expiration_date):
        self.name = name
        self.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")

    def days_until_expired(self):
        return (self.expiration_date - datetime.now()).days

    def get_color(self):
        days = self.days_until_expired()
        if days < 0:
            return "red"
        elif days <= 2:
            return "orange"
        elif days <= 5:
            return "yellow"
        else:
            return "green"

# -------- Main App --------
class ExpirationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expiration Tracker")
        self.root.geometry("3840x2160")
        self.items = [] 
        self.current_view = 'list'

        # Frames
        self.list_frame = tk.Frame(root)
        self.card_frame = tk.Frame(root)
        self.detail_frame = tk.Frame(root)

        self.create_list_view()
        self.create_card_view()
        self.create_detail_view()

        self.show_list_view()

    # -------- List View --------
    def create_list_view(self):
        top_bar = tk.Frame(self.list_frame)
        top_bar.pack(fill=tk.X, pady=5)

        toggle_btn = tk.Button(top_bar, text="Switch to Card View", command=self.show_card_view)
        toggle_btn.pack(side=tk.LEFT, padx=10)

        add_btn = tk.Button(top_bar, text="Add Item", command=self.add_item_popup)
        add_btn.pack(side=tk.RIGHT, padx=10)

        # Scrollable canvas
        self.list_canvas = tk.Canvas(self.list_frame, bg="white")
        scrollbar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.list_canvas.yview)
        self.list_items_frame = tk.Frame(self.list_canvas, bg="white")

        self.list_items_frame.bind(
            "<Configure>",
            lambda e: self.list_canvas.configure(
                scrollregion=self.list_canvas.bbox("all")
            )
        )

        self.list_canvas.create_window((0, 0), window=self.list_items_frame, anchor="nw")
        self.list_canvas.configure(yscrollcommand=scrollbar.set)

        self.list_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # -------- Card View --------
    def create_card_view(self):
        top_bar = tk.Frame(self.card_frame)
        top_bar.pack(fill=tk.X, pady=5)

        toggle_btn = tk.Button(top_bar, text="Switch to List View", command=self.show_list_view)
        toggle_btn.pack(side=tk.LEFT, padx=10)

        add_btn = tk.Button(top_bar, text="Add Item", command=self.add_item_popup)
        add_btn.pack(side=tk.RIGHT, padx=10)

        self.cards_container = tk.Frame(self.card_frame, bg="white")
        self.cards_container.pack(fill=tk.BOTH, expand=True)

    # -------- Detail View --------
    def create_detail_view(self):
        self.detail_label = tk.Label(self.detail_frame, text="", font=("Arial", 28), justify="left")
        self.detail_label.pack(pady=30)

        back_btn = tk.Button(self.detail_frame, text="Back", font=("Arial", 20), command=self.back_to_previous_view)
        back_btn.pack(pady=10)

    # -------- Popups & Add --------
    def add_item_popup(self):
        name = simpledialog.askstring("Add Item", "Enter item name:")
        if not name:
            return

        expiration_date = simpledialog.askstring("Add Item", "Enter expiration date (YYYY-MM-DD):")
        try:
            item = Item(name, expiration_date)
            self.items.append(item)
            self.refresh_views()
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format.")

    # -------- Update both views --------
    def refresh_views(self):
        # List View
        for widget in self.list_items_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.items):
            color = item.get_color()
            days = item.days_until_expired()
            text = f"{item.name} - Expires in {days} days"
            btn = tk.Button(
                self.list_items_frame,
                text=text,
                bg=color,
                fg="black",
                font=("Arial", 16),
                height=2,
                command=lambda i=item: self.show_detail_view(i)
            )
            btn.pack(fill=tk.X, padx=10, pady=5)

        # Card View
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        row = 0
        col = 0
        for item in self.items:
            color = item.get_color()
            days = item.days_until_expired()
            frame = tk.Frame(self.cards_container, bg=color, bd=2, relief=tk.RAISED)
            frame.grid(row=row, column=col, padx=20, pady=20, ipadx=20, ipady=20)

            label = tk.Label(
                frame,
                text=f"{item.name}\nExpires in {days} days",
                bg=color,
                fg="black",
                font=("Arial", 18),
                justify="center",
                wraplength=150
            )
            label.pack(padx=10, pady=10)

            btn = tk.Button(
                frame,
                text="View",
                font=("Arial", 16),
                command=lambda i=item: self.show_detail_view(i)
            )
            btn.pack(pady=5)

            col += 1
            if col >= 3:
                col = 0
                row += 1

    # -------- View Handlers --------
    def show_list_view(self):
        self.card_frame.pack_forget()
        self.detail_frame.pack_forget()
        self.list_frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = 'list'
        self.refresh_views()

    def show_card_view(self):
        self.list_frame.pack_forget()
        self.detail_frame.pack_forget()
        self.card_frame.pack(fill=tk.BOTH, expand=True)
        self.current_view = 'card'
        self.refresh_views()

    def show_detail_view(self, item):
        self.list_frame.pack_forget()
        self.card_frame.pack_forget()

        days = item.days_until_expired()
        detail_text = (
            f"Item: {item.name}\n"
            f"Expiration: {item.expiration_date.strftime('%Y-%m-%d')}\n"
            f"Days Left: {days}"
        )
        self.detail_label.config(text=detail_text)
        self.detail_frame.pack(fill=tk.BOTH, expand=True)

    def back_to_previous_view(self):
        self.detail_frame.pack_forget()
        if self.current_view == 'list':
            self.show_list_view()
        else:
            self.show_card_view()

# -------- Run --------
root = tk.Tk()
app = ExpirationApp(root)
root.mainloop()
