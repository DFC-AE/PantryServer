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

# Main application class for "The Pantry"
class ExpirationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expiration Tracker")

        # Make the window full-screen
        self.root.attributes("-fullscreen", True)

        self.items = []  # List to hold Item objects

        # Main container frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Left-side frame to display the item list
        self.list_frame = tk.Frame(self.main_frame, bg="lightgray", width=300)
        self.list_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Canvas and scrollbar setup for scrollable item list
        self.canvas = tk.Canvas(self.list_frame, bg="lightgray")
        self.scrollbar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="lightgray")

        # Update scroll region when content changes.
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        # Embed the scrollable frame into the canvas
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas and scrollbar into list_frame
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create "+" button in top-right to add new items
        self.add_button = tk.Button(self.main_frame, text="+", font=("Arial", 24), command=self.add_item_popup)
        self.add_button.pack(anchor='ne', padx=20, pady=20)


    # Popup to ask the user for item name and expiration date
    def add_item_popup(self):
        name = simpledialog.askstring("Add Item", "Enter item name:")
        if not name:
            return  # If canceled or empty, do nothing

        expiration_date = simpledialog.askstring("Add Item", "Enter expiration date (YYYY-MM-DD):")
        try:
            item = Item(name, expiration_date)  # Create new item
            self.items.append(item)             # Add to item list
            self.update_list()                  # Refresh the display
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter the date in YYYY-MM-DD format.")

     # Edit list of items
    def edit_item_popup(self, index):
        item = self.items[index]

        # Ask user for new name (pre-filled with current)
        new_name = simpledialog.askstring("Edit Item", "Update name:", initialvalue=item.name)
        if new_name is None:
            return  # Cancelled

        # Ask user for new expiration date (pre-filled with current)
        new_date_str = simpledialog.askstring(
            "Edit Item",
            "Update expiration date (YYYY-MM-DD):",
            initialvalue=item.expiration_date.strftime("%Y-%m-%d")
        )

        try:
            # Update item values
            self.items[index].name = new_name
            self.items[index].expiration_date = datetime.strptime(new_date_str, "%Y-%m-%d")
            self.update_list()
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter the date in YYYY-MM-DD format.")

            
        # Update the list display with current items, sorted by expiration
    def update_list(self):
        # Clear existing item widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Sort items from soonest to latest expiration
        self.items.sort(key=lambda item: item.expiration_date)

        # Display each item with its color-coded expiration status
        for idx, item in enumerate(self.items):
            color = item.get_color()
            display_text = f"{item.name} - Expires: {item.expiration_date.strftime('%Y-%m-%d')}"

            # Frame to hold label + edit button
            item_frame = tk.Frame(self.scrollable_frame, bg=color)
            item_frame.pack(fill=tk.X, padx=5, pady=2)

            # Label showing the item details
            label = tk.Label(
                item_frame,
                text=display_text,
                bg=color,
                fg="black",
                anchor="w",
                width=30,
                padx=10,
                pady=5
            )
            label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Edit button
            edit_btn = tk.Button(
                item_frame,
                text="Edit",
                command=lambda index=idx: self.edit_item_popup(index),
                bg="white"
            )
            edit_btn.pack(side=tk.RIGHT, padx=5)


# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ExpirationApp(root)
    root.mainloop()
