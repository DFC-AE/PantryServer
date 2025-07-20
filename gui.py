## Import Libraries ##
import tkinter as tk
from tkinter import simpledialog, Button, Label
from datetime import datetime, timedelta
from tkcalendar import *
import cv2
from PIL import Image, ImageTk

## Quit with Esc ##
root = tk.Tk()
root.bind('<Escape>', lambda e: root.quit())

## Quit with Esc ##
#app = tk.Tk()
#app.bind('<Escape>', lambda e: app.quit())

## Add Calendar ##
cal = DateEntry(root, date_pattern="yyyy-mm-dd")
cal.pack(padx=10, pady=10)

## Automatically Get Current Date ##
def get_date():
	selected_date = cal.get()
	print(f"Selected Date: {selected_date}")

## Add Button and Label ##
#Button(root,
#	text= "Click Here to Input Selected Date",
#	command = get_date).pack(pady = 10)

### Light and Dark Mode Toggle ###
switch_value = True

## Toggle Function ##
def toggle():
        global switch_value
        if switch_value == True:
                switch.config(#image=dark,
                                text="Light Mode",
                                background="#26242f",
                                foreground="white",
                                activeforeground="red",
                                activebackground="white")
                                #activebackground="#26242f")

                ## Change Window to Light Theme ##
#                window.config(background="#26242f")
                root.config(background="#26242f")
#                self.list_canvas = tk.Canvas(list_frame, background="#26242f")
#                self.list_items_frame = tk.Frame(self.list_canvas, bg="#26242f")
                switch_value = False

        else:
                switch.config(#image=light,
                                text="Dark Mode",
                                background="white",
                                foreground="black",
                                activeforeground="blue",
                                #activebackground="white")
                                activebackground="#26242f")

                ## Change Window to Dark Theme ##
#                window.config(background="white")
                root.config(background="white")
#                self.list_canvas = tk.Canvas(list_frame, background="white")
#                self.list_items_frame = tk.Frame(self.list_canvas, bg="white")
                switch_value = True

### Buttons and Switches ###

## Create Light Dark Button ##
#switch = Button(window,
switch = Button(root,
#               image=light,
		text="Dark Mode",
#                borderwidth=0,
                background="white",
#		foreground="#26242f",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
		anchor="w",
                command=toggle)
## Position Toggle Button ##
switch.pack(padx=10, pady=10)

## Create Item Button ##
#switch = Button(window,
switch = Button(root,
#               image=light,
		text="Add Item",
#                borderwidth=0,
                background="white",
#		foreground="#26242f",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
#		side=tk.BOTTOM,
		anchor="center",
#                command=add_item_popup)
                command=toggle)
## Position Toggle Button ##
switch.pack(padx=10, pady=10)

## Create View Button ##
#switch = Button(window,
switch = Button(root,
#               image=light,
		text="View",
#                borderwidth=0,
                background="white",
#		foreground="#26242f",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
		anchor="e",
#                command=show_card_view)
                command=toggle)
## Position Toggle Button ##
switch.pack(padx=10, pady=10)

### Camera Input ###
cpt = cv2.VideoCapture(0)
cpt_wdt, cpt_hgt = 360, 360
cpt.set(cv2.CAP_PROP_FRAME_WIDTH, cpt_wdt)
cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, cpt_hgt)

#label_widget = Label(app)
#label_widget.pack()

def open_camera():
	## Capture Video Frame by Frame ##
	_, frame = vid.read()

	## Translate Color Space ##
	opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

	## Capture Last Frame ##
	captured_image = Image.fromarray(opencv_image)

	## Convert Image to PhotoImage ##
	photo_image = ImageTk.PhotoImage(image=captured_image)

	## Display PhotoImage in Label ##
	label_widget.photo_image = photo_image

	## Configure Label Image ##
	label_widget.configure(image=photo_image)

	## Repeat on 10 Second Loop ##
	label_widget.after(10, open_camera)

## Camera Button ##
#cam_btn = Button(app,
cam_btn = Button(root,
		text="Open Scanner",
		command=open_camera)
cam_btn.pack()

# Class to represent each item (food/drink) with name and expiration date
class Item:
    def __init__(self, name, expiration_date):
        self.name = name
        self.expiration_date = datetime.strptime(expiration_date, "%Y-%m-%d")

    # Calculate how many days until the item expires
    def days_until_expired(self):
        return (self.expiration_date - datetime.now()).days + 1


    # Return a color based on how close the item is to expiring
    def get_color(self):
        days = self.days_until_expired() - 1
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

# -------- Main App --------
class ExpirationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expiration Tracker")
        self.root.geometry("1024x600")
        self.root.attributes("-fullscreen", False)
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

        add_btn = tk.Button(top_bar, text="Dark Mode", command=toggle)
        add_btn.pack(side=tk.RIGHT, padx=10)

        add_btn = tk.Button(top_bar, text="Add Item", command=self.add_item_popup)
        add_btn.pack(side=tk.BOTTOM, padx=10)

        ## Add Calendar ##
        cal = DateEntry(top_bar, date_pattern="yyyy-mm-dd")
        cal.pack(padx=10, pady=10)

        # Scrollable canvas
#        self.list_canvas = tk.Canvas(self.list_frame, bg="white")
        self.list_canvas = tk.Canvas(self.list_frame, bg="#26242f")
        scrollbar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.list_canvas.yview)
#        self.list_items_frame = tk.Frame(self.list_canvas, bg="white")
        self.list_items_frame = tk.Frame(self.list_canvas, bg="#26242f")

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
        add_btn.pack(side=tk.TOP, padx=10)

        add_btn = tk.Button(top_bar, text="Dark Mode", command=toggle)
        add_btn.pack(side=tk.RIGHT, padx=10)

        # Card view scrollbar
#        self.card_canvas = tk.Canvas(self.card_frame, bg="white")
        self.card_canvas = tk.Canvas(self.card_frame, bg="#26242f")
        card_scrollbar = tk.Scrollbar(self.card_frame, orient=tk.VERTICAL, command=self.card_canvas.yview)
#        self.cards_container = tk.Frame(self.card_canvas, bg="white")
        self.cards_container = tk.Frame(self.card_canvas, bg="#26242f")

        self.cards_container.bind(
            "<Configure>",
            lambda e: self.card_canvas.configure(scrollregion=self.card_canvas.bbox("all"))
        )

        self.card_canvas.create_window((0, 0), window=self.cards_container, anchor="nw")
        self.card_canvas.configure(yscrollcommand=card_scrollbar.set)

        self.card_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        card_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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

#        expiration_date = simpledialog.askstring("Add Item", "Enter expiration date (YYYY-MM-DD):")
#        expiration_date = selected_date
        expiration_date = cal.get()
        try:
            item = Item(name, expiration_date)
            self.items.append(item)
            self.refresh_views()
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format.")

    # -------- Update both views --------
    def refresh_views(self):
        # List View
        self.items.sort(key=lambda item: item.expiration_date)
        for widget in self.list_items_frame.winfo_children():
            widget.destroy()

        for idx, item in enumerate(self.items):
            color = item.get_color()
            days = item.days_until_expired()
	    ## Expiring ##
            if days == 1 :
                text = f"{item.name} - Expires tomorrow"
            elif days == 0 :
                text = f"{item.name} - Expires today"
            elif days > 1 :
                text = f"{item.name} - Expires in {check_dates(days)} days"
            ## Expired ##
            elif days == -1 :
                color = "#FF0000"
                text = f"{item.name} - Expired yesterday"
            else:
                color = "#FF0000"
                text = f"{item.name} - Expired {check_dates(days)} days ago"
            l_btn = tk.Button(
                self.list_items_frame,
                text=text,
                bg=color,
                fg="black",
                font=("Arial", 16),
                height=2,
                command=lambda i=item: self.show_detail_view(i)
            )
            l_btn.pack(fill=tk.X, padx=10, pady=5)

        # Card View
        for widget in self.cards_container.winfo_children():
            widget.destroy()

        row = 0
        col = 0
        for item in self.items:
            color = item.get_color()
            days = item.days_until_expired()
            if days >= 0 :
                text = f"{item.name} - Expires in {check_dates(days)} days"
            else:
                color = "#FF0000"
                text = f"{item.name} - Expired {check_dates(days)} days ago" 
                           
            c_btn = tk.Button(
                self.cards_container,
                text= text,
                bg=color,
                fg="black",
                font=("Arial", 18),
                justify="center",
                wraplength=150 ,
                command=lambda i=item: self.show_detail_view(i)
            )
            c_btn.grid(row=row, column=col, padx=20, pady=20, ipadx=20, ipady=20)

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
            f"Days Left: {check_dates}"
        )
        days_left_counter = lambda days: days if days > 0 else "0"
        detail_text = (
            f"Item: {item.name}\n"
            f"Expiration: {item.expiration_date.strftime('%Y-%m-%d')}\n"
            f"Days Left: {days_left_counter(days)}"
        )
        self.detail_label.config(text=detail_text)
        self.detail_frame.pack(fill=tk.BOTH, expand=True)

    def back_to_previous_view(self):
        self.detail_frame.pack_forget()
        if self.current_view == 'list':
            self.show_list_view()
        else:
            self.show_card_view()

# -------- Makes sure the dates aren't negative-----
def check_dates(days):
    if days >= 0 :
        return days
    else:
        return days * -1

# -------- Run --------
#root = tk.Tk()
app = ExpirationApp(root)
root.mainloop()
