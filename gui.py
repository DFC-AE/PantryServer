## Import Libraries ##
import tkinter as tk
from tkinter import simpledialog, Button, Frame, Label, PhotoImage, Toplevel, messagebox
## For Calendar ##
from datetime import datetime, timedelta
from tkcalendar import *
## For Camera ##
import cv2
from PIL import Image, ImageTk
## For Restart ##
import os
import sys
import shutil
## Barcode Scanner ##
from pyzbar.pyzbar import decode
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
## For Random Background ##
import random

### Create Home Page ###
root = tk.Tk()

### Create Splash Screen ###
## Import Splash Screen Image ##
img_wdt = 50
img_hgt = 50

## Create Splash Screen ##
splash_root = tk.Tk()
splash_root.geometry("500x500")
splash_label = Label(splash_root,
			text="Splash Screen",
			font=500)
#			image="frigImg")
splash_label.pack()

def splash():
	## Destory Splash Window ##
	splash_root.quit()
#	splash_root.destory()

splash_root.after(5000, splash)

### Home Page Adjustments ###
## Geeek Pi ##
root.geometry("480x320")
root.wm_attributes("-fullscreen")

## Frames ##
list_frame = tk.Frame(root)
card_frame = tk.Frame(root)
detail_frame = tk.Frame(root)

### Import and Resize Random Background Image ##
def get_random_image(backgrounds):
	try:
		files = os.listdir(backgrounds)
		## Choose Random Image ##
		random_image = random.choice(backgrounds)
		random_image_path = os.path.join(backgrounds, random_image)
		print(f"Selected Background Image:")
		return random_image_path
	except Exception as e:
		print(f"Failed to Select Random Background Image: {e}")
		return None

def display_background(backgrounds):
	try:
		if backgrounds and os.path.isfile(backgrounds):
			with Image.open(backgrounds) as img:
				img.show()
				print(f"Displayed image: {backgrounds}")
		else:
			print(f"Invalid Image Path: {backgrounds}")
	except Exception as e:
		print(f"An Error Occurred while Displaying the Image: {e}")

### Import and Resize Background Image ##
## Background Size ##
bck_wdt = 1080
bck_hgt = 1920

img_back = Image.open("pics/back.jpg")


## Open Background Image ##
img_back = img_back.resize((bck_wdt, bck_hgt), Image.LANCZOS)
backImg = ImageTk.PhotoImage(img_back)

## Create Background ##
background = Label(root,
		image = backImg)

background.place(x=0, y=0)
## Background Greeting ##
welcome = Label(root,
		text = " Welcome to your Pantry Companion ",
		font=("Comic Sans", 33)).pack()


### Import and Resize Button Images ###
## Button Size ##
img_wdt = 50
img_hgt = 50
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
## Camera Image ##
img_cam = Image.open("pics/cam.jpg")
img_cam = img_cam.resize((img_wdt, img_hgt), Image.LANCZOS)
camImg = ImageTk.PhotoImage(img_cam)
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
img_code = cv2.imread("pics/barcode.png")
## Code ##
img_scan1 = Image.open("pics/barcode.png")
img_scan1 = img_scan1.resize((300, 100), Image.Resampling.LANCZOS)
img_scan2 = ImageTk.PhotoImage(img_scan1)

## Quit with Esc ##
root.bind('<Escape>', lambda e: root.quit())


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

## Restart with Tab ##
root.bind('<Prior>', lambda e: restart_program())

## Add Calendar ##
cal = DateEntry(root, date_pattern="yyyy-mm-dd")
cal.pack(padx=10, pady=10)

## Automatically Get Current Date ##
def get_date():
	selected_date = cal.get()
	print(f"Selected Date: {selected_date}")

### Light and Dark Mode Toggle ###
switch_value = True

## Toggle Function ##
def toggle():
        global switch_value
        if switch_value == True:
                switch.config(#image="lightImg",
                                text="Light Mode",
                                background="#26242f",
                                foreground="white",
                                activeforeground="red",
                                activebackground="white")
                                #activebackground="#26242f")

                ## Change Window to Light Theme ##
                root.config(background="#26242f")
                list_canvas = tk.Canvas(list_frame, background="#26242f")
                list_items_frame = tk.Frame(list_canvas, bg="#26242f")
                switch_value = False

        else:
                switch.config(#image="lightImg",
                                text="Dark Mode",
                                background="white",
                                foreground="black",
                                activeforeground="blue",
                                #activebackground="white")
                                activebackground="#26242f")

                ## Change Window to Dark Theme ##
                root.config(background="white")
                list_canvas = tk.Canvas(list_frame, background="white")
                list_items_frame = tk.Frame(list_canvas, bg="white")
                switch_value = True

## Test Button ##
switch = Button(root,
	image=homeImg,
	width=50,
	command=toggle)
switch.pack(side='bottom', padx=10, pady=10)

## Add Item ##
items = []

## Import Old Item Data ##
try:
	items_old = open("items.txt", "r").read().split('\n')
	items.extend(items_old)
except:
	print ("Unable to Load Previously Input Item List")
	items = []

## Add Item Function ##
def add_item():
	name = simpledialog.askstring("Add Item", "Enter item name:")
	if not name:
		return

	expiration_date = cal.get()
	try:
		item = Item(name, expiration_date)
#		self.items.append(item)
#		self.refresh_views()
		items.append(item)
		## Open Previous List ##
		with open('items.txt', 'w+') as i:
			## Write Elements to List ##
			for item in items:
				i.write('%s\n' %items)
			print("Items Documented Successfully")

		## Close Item File ##
		i.close()

	except ValueError:
		tk.messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format.")


### Camera Input ###
cpt = cv2.VideoCapture(0)
## Resolution ##
cpt_wdt = 1920
cpt_hgt = 1080
cpt.set(cv2.CAP_PROP_FRAME_WIDTH, cpt_wdt)
cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, cpt_hgt)

## Internal ##
cam_widget = tk.Label(root,
#			textvariable="test",
			background="black",
#			justify="left",
			cursor="hand2")
#cam_widget.pack()
cam_widget.pack(fill = "both")
cam_widget.bind('<Next>'), lambda e: cam_widget.quit()

def open_camera():
	## Capture Video Frame by Frame ##
	_, frame = cpt.read()

	## Translate Color Space ##
	opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

	## Capture Last Frame ##
	captured_image = Image.fromarray(opencv_image)

	## Convert Image to PhotoImage ##
	photo_image = ImageTk.PhotoImage(image=captured_image)

	## Display PhotoImage in Label ##
	cam_widget.photo_image = photo_image

	## Configure Label Image ##
	cam_widget.configure(image=photo_image)

	## Repeat on 1 Second Loop ##
	cam_widget.after(1, open_camera)

	## Close Video with ESC ##
#	if cv2.waitKey(10) == 27:
#		break
	cam_widget.bind('<Insert>', lambda e: cam_widget.quit())

### Barcode Scanner ###
def detect_barcode(image):
	## Code in Testing ##
	## Capture Video Frame by Frame ##
	_, frame = cpt.read()

	## Translate Color Space ##
	opencv_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

	## Capture Last Frame ##
	captured_image = Image.fromarray(opencv_image)

	## Convert Image to PhotoImage ##
	photo_image = ImageTk.PhotoImage(image=captured_image)

	## Previous Working Code ##
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	## Detect Barcode ##
	barcodes = decode(gray)

	## Loop through Codes ##
	for barcode in barcodes:
		## Extract Data ##
		barcode_data = barcode.data.decode("utf-8")
		barcode_type = barcode.type

		## Print Barcode Data ##
		print("Barcode Data:", barcode_data)
		print("Barcode Type:", barcode_type)

		## Encompass Barcode ##
		(x, y, w, h) = barcode.rect
		cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

		## Place Data on Image ##
		cv2.putText(image, f"{barcode_data} ({barcode_type})",
		(x, y - 10),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

		## Convert Image from BGR to RGB ##
		image_rgb = cv2.cvtColor(image,
					cv2.COLOR_BGR2RGB)
		show_barcode(image_rgb)

## Show Barcode ##
def show_barcode(image):
	plt.imshow(image)
	plt.axis('off')
	plt.title('Scanned Barcode:', fontweight ="bold")
	plt.show()
      
## Open with Button ##
def open_window_scan():
	window_scan = Toplevel(root)
	window_scan.title("Barcode Window")
	window_scan.geometry("300x100")

	Label(window_scan,
		image=img_scan2).pack(pady=20)

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
#        self.root.geometry("1024x600")
        self.root.geometry("1024x600")
        self.root.attributes("-fullscreen", False)
        self.items = []
	## Import Old Item Data ##
#        try:
#               items_old = open("items.txt", "r").read().split('\n')
#               self.items.extend(items_old)
#        except:
#               print ("Unable to Load Previously Input Item List")
#               selt.items = []

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
        add_btn.pack(side=tk.TOP, padx=10)

        self.list_canvas = tk.Canvas(self.list_frame, bg="#26242f")
        self.list_items_frame = tk.Frame(self.list_canvas, bg="#26242f")
        scrollbar = tk.Scrollbar(self.list_frame, orient=tk.VERTICAL, command=self.list_canvas.yview)

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

        self.card_canvas = tk.Canvas(self.card_frame, bg="#26242f")
        card_scrollbar = tk.Scrollbar(self.card_frame, orient=tk.VERTICAL, command=self.card_canvas.yview)
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
        self.detail_label = tk.Label(self.detail_frame, text="", font=("Arial", 15), justify="left")
        self.detail_label.pack(pady=30)

        back_btn = tk.Button(self.detail_frame, text="Back", font=("Arial", 15), command=self.back_to_previous_view)
        back_btn.pack(side='bottom', padx=10, pady=10)

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

    # -------- Popups & Add --------
    def add_item_popup(self):
        name = simpledialog.askstring("Add Item", "Enter Item Name:")
        if not name:
            return

        expiration_date = cal.get()
        try:
            item = Item(name, expiration_date)
            self.items.append(item)
            ## Open Previous List ##
            with open('items.txt', 'w+') as i:
                        ## Write Elements to List ##
                        for item in items:
                               i.write('%s\n' %items)
                        print("Items Documented Successfully")

            ## Close Item File ##
            i.close()
            self.refresh_views()
        except ValueError:
            tk.messagebox.showerror("Error", "Please Enter Date in YYYY-MM-DD Format.")

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

    ## item sort button ##
    def sort_items(self, sort_type):
        if sort_type == "Expiration (Soonest)":
            self.items.sort(key=lambda x: x.expiration_date)
        elif sort_type == "Expiration (Latest)":
            self.items.sort(key=lambda x: x.expiration_date, reverse=True)
        elif sort_type == "Name (A-Z)":
            self.items.sort(key=lambda x: x.name.lower())
        elif sort_type == "Name (Z-A)":
            self.items.sort(key=lambda x: x.name.lower(), reverse=True)
        self.create_list_view()

    ## item delete button ##
    def delete_item(self, item):
        if messagebox.askyesno("Delete", f"Delete {item.name}?"):
            self.items.remove(item)
            self.save_items()
            self.create_list_view()
            
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

        back_btn = tk.Button(self.root, text="Back", font=("Arial", 16), command=self.create_tracker_ui)
        back_btn.pack(pady=10)

        scan_btn = tk.Button(self.root, text="Scan Barcode", command=self.open_camera)
        scan_btn.pack(pady=10)

        manual_btn = tk.Button(self.root, text="Enter Barcode", command=lambda: self.manual_barcode_entry(item))
        manual_btn.pack(pady=10)

        edit_btn = tk.Button(self.root, text="Edit Item", command=lambda: self.edit_item(item))
        edit_btn.pack(pady=10)

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

### Buttons and Switches ###

## Create Item Button ##
#switch = Button(window,
btn_item = Button(root,
               image=itemImg,
#		text="Add Item",
#                borderwidth=0,
                background="white",
#		foreground="#26242f",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
#		side=tk.BOTTOM,
#		anchor="center",
		anchor="n",
		cursor="hand2",
                command=add_item)
btn_item.pack(padx=10, pady=10)

## Create Camera Button ##
btn_cam = Button(root,
               image=camImg,
#		text="Add Item",
#                borderwidth=0,
                background="white",
#		foreground="#26242f",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
#		side=tk.BOTTOM,
		anchor="center",
		cursor="hand2",
                command=open_camera)
#btn_cam.pack(side='left', padx=10, pady=10)
btn_cam.pack(side='right', padx=10, pady=10)

## Create Scan Button ##
btn_scan = Button(root,
               image=scanImg,
                background="white",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
		anchor="center",
		cursor="hand2",
                command=detect_barcode(img_code))

btn_scan.pack(side='right', padx=10, pady=10)

## Create Light Dark Button ##
btn_mode = Button(root,
               image=lightImg,
                background="white",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
		anchor="e",
		cursor="hand2",
                command=toggle)
btn_mode.pack(side='left', padx=10, pady=10)

## Create View Button ##
btn_view = Button(root,
               image=viewImg,
                background="white",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
		anchor="w",
		cursor="hand2",
		command=open_window_scan)
btn_view.pack(side='left', padx=10, pady=10)

# -------- Run --------
#root = tk.Tk()
app = ExpirationApp(root)
root.mainloop()

## Save Item Input to List or Discard ##
#try:
#	with open("items.txt", "w") as out:
#	with open("items.txt", "a") as out:
#		out.write('\n'.join(items))
#except:
#	print ("Unable to Write Data. Discarding...")
