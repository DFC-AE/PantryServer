## Import Libraries ##
import tkinter as tk
from tkinter import simpledialog, Button, Frame, Label, PhotoImage, Toplevel
## For Calendar ##
from datetime import datetime, timedelta
#from tkcalendar import *
from tkcalendar import DateEntry
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
#root.attributes('-fullscreen', True)

### Create Splash Screen ###
## Import Splash Screen Image ##
splash_wdt = 50
splash_hgt = 50
img_splash = Image.open("pics/frig_fog.jpg")
img_splash = img_splash.resize((splash_wdt, splash_hgt), Image.LANCZOS)
splashImg = ImageTk.PhotoImage(img_splash)
## Create Splash Screen Window ##
splash_root = tk.Tk()
#splash_root = root.Tk()
splash_root.geometry("500x500")
splash_label = Label(splash_root,
			text="Splash Screen",
			font=500)
#			image=splashImg)
splash_label.pack()

def splash():
	## Destory Splash Window ##
	splash_root.quit()
#	splash_root.destory()

splash_root.after(500, splash)

### Create Home Page ###
#root = tk.Tk()

### Home Page Adjustments ###
## Geeek Pi ##
root.geometry("480x320")
## 1080 ##
#root.geometry("1920x1080")
## Resize to Background Image ##
#root.geometry("%dx%d" % (bck_wdt, bck_hgt))
## Transparency ##
#root.wm_attributes("-fullscreen", 'black')
root.wm_attributes("-fullscreen")

## Frames ##
list_frame = tk.Frame(root)
card_frame = tk.Frame(root)
detail_frame = tk.Frame(root)

### Import and Resize Random Background Image ##
def get_random_image(backgrounds):
	try:
		files = os.listdir(backgrounds)
		## Filter to only Select Images ##
#		images = [file for file in files
#				if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
#				if not images:
#					print("No Background Image Found")
#					return None
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
## Geeek Pi ##
#bck_wdt = 320
#bck_hgt = 460
## 720 ##
#bck_wdt = 720
#bck_hgt = 1280
## 1080 ##
bck_wdt = 1080
bck_hgt = 1920

## Randomly Select Background Image ##
#img_back = Image.open("pics/back.jpeg")
img_back = Image.open("pics/back.jpg")
#img_back = Image.open("get_background_image()")
#back = os.listdir("backgrounds")
#random_back = random.choice("back")
#random_back_path = os.path.join("backgrounds", random_back)
#random_back_path = os.path.join(folder_path, random_back)
#print(f"random_back_path")

## Open Background Image ##
#img_back = Image.open("random_back_path")
#img_back = Image.open(random_back)
#img_back = Image.open(os.listdir("backgrounds"))
#img_back = Image.open(get_random_image("backgrounds"))

img_back = img_back.resize((bck_wdt, bck_hgt), Image.LANCZOS)
backImg = ImageTk.PhotoImage(img_back)
#backImg = ImageTk.PhotoImage(random.choice("backgrounds"))

## Create Background ##
background = Label(root,
		image = backImg)
#		image = get_background_image())
#		image = random_image_path)
background.place(x=0, y=0)
## Background Greeting ##
welcome = Label(root,
		text = " Welcome to your Pantry Companion ",
		font=("Comic Sans", 33)).pack()
#welcome.pack(pady = 20)

## Create Background Grid ##
#frame_left = Frame(root,
#		width=200,
#		height=200,
#		background='grey')
#frame_left.grid(row=0, column=0, padx=10, pady=5)
#frame_right = Frame(root,
#		width=650,
#		height=400,
#		background='grey')
#frame_right.grid(row=0, column=1, padx=10, pady=5)

### Import and Resize Button Images ###
#light = PhotoImage(file="light.png")
## Button Size ##
img_wdt = 50
img_hgt = 50
#dark = Image.open("light.png")
## Light Image ##
img_light = Image.open("pics/light.png")
img_light = img_light.resize((img_wdt, img_hgt), Image.LANCZOS)
lightImg = ImageTk.PhotoImage(img_light)
## Fridge Image ##
#img_frig = Image.open("pics/frig.jpg")
#img_frig = img_frig.resize((img_wdt, img_hgt), Image.LANCZOS)
#frigImg = ImageTk.PhotoImage(img_frig)
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
#root.bind('<Escape>', lambda e: root.destroy())

## Quit with Esc ##
#app = tk.Tk()
#app.bind('<Escape>', lambda e: app.quit())

def restart_program():
#	os.execv(sys.argv[0], sys.argv)
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
                switch.config(#image="lightImg",
                                text="Light Mode",
                                background="#26242f",
                                foreground="white",
                                activeforeground="red",
                                activebackground="white")
                                #activebackground="#26242f")

                ## Change Window to Light Theme ##
#                window.config(background="#26242f")
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
#                window.config(background="white")
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
#def add_item_popup(self):
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

#        expiration_date = simpledialog.askstring("Add Item", "Enter expiration date (YYYY-MM-DD):")
#        expiration_date = selected_date
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

		## Save Item Input to List or Discard ##
#		try:
#			with open("items.txt", "w") as out:
#			with open("items.txt", "a") as out:
#				out.write('\n'.join(items))
#		except:
#			print ("Unable to Write Data. Discarding...")

#		refresh_views()
	except ValueError:
		tk.messagebox.showerror("Error", "Please enter date in YYYY-MM-DD format.")


### Camera Input ###
cpt = cv2.VideoCapture(0)
## Resolution ##
cpt_wdt = 1920
cpt_hgt = 1080
#cpt_wdt = 600
#cpt_hgt = 480
cpt.set(cv2.CAP_PROP_FRAME_WIDTH, cpt_wdt)
cpt.set(cv2.CAP_PROP_FRAME_HEIGHT, cpt_hgt)

## Create External Camera Window ##
#cam = tk.Tk()

## Quit Camera with Home Key ##
#cam.bind('<Home>', lambda e: cam.quit())

## Create Camera Widget ##
## External ##
#cam_widget = Label(cam,
#cam_widget = tk.Label(cam,
## Internal ##
cam_widget = tk.Label(root,
#			textvariable="test",
			background="black",
#			justify="left",
			cursor="hand2")
#cam_widget.pack()
cam_widget.pack(fill = "both")
#root.label_widget = Label(root)
#root.label_widget.pack()

## Bind q to Quit Camera ##
#root.bind('<Next>'), lambda e: cam_widget.quit()
cam_widget.bind('<Next>'), lambda e: cam_widget.quit()
#cam_widget.bind('<Next>'), lambda e: cam_widget.destroy()
#root.bind('<q>'), lambda e: cpt.quit()

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


### Camera Buttons ###
## Open Button ##
#cam_btn = Button(app,
#cam_btn = Button(root,
#		text="Open Scanner",
#		command=open_camera)
#cam_btn.pack()
## Close Button ##
#cam_btn = Button(root,
#		text="Close Scanner",
#		text="Restart Program",
#		command=restart_program)
#cam_btn.pack()

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
#	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

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

#	def show_barcode(image):
#		plt.imshow(image_rgb)
	#	plt.imshow(img_code)
#		plt.axis('off')
#		plt.show()

		show_barcode(image_rgb)
		open_window_scan(image_rgb)

## Open with Button ##
def open_window_scan(image):
	## Create Barcode Window ##
	window_scan = Toplevel(root)
	window_scan.title("Barcode Window")
	window_scan.geometry("300x100")

	## Convert Image to PhotoImage ##
#	scan_image = ImageTk.PhotoImage(image=img_code)
	scan_image = ImageTk.PhotoImage(img_scan1)

	Label(window_scan,
		image=img_scan2).pack(pady=20)
#		image=scan_image).pack(pady=20)
#		image=image).pack(pady=20)

## Show Barcode ##
def show_barcode(image):
	## The Figure to Contain the Barcode ##
#	fig = Figure(figsize = (5, 5), dpi = 100)

	## Create Tkinter Canvas for Barcode ##
#	canvas_code = FigureCanvasTkAgg(fig, master = window_code)
#	canvas_code.draw()

	## Place Canvas Inside Tkinter Window ##
#	canvas_code.get_tk_widget().pack()

	## Creating the Matplotlib Toolbar ##
#	toolbar = NavigationToolbar2Tk(canvas_code, window_code)
#	toolbar.update()

	## Place Toolbar inside Tkinter Window ##
#	canvas_code.get_tk_widget().pack()

#	plt.imshow(image_rgb)
#	plt.imshow(img_code)
	plt.imshow(image)
	plt.axis('off')
	plt.title('Scanned Barcode:', fontweight ="bold")
	plt.show()
#	plt.show(root)
#	root.plt.imshow(image)
#	root.plt.axis('off')
#	root.plt.title('Scanned Barcode:', fontweight ="bold")
#	root.plt.show()

### Open Barcode Window ###
## Barcode Window ##
#window_code = tk()
#window_code = tk.Tk()
#window_code.title('Scanned Barcode')
#window_code.geometry("250x250")
#window_code.mainloop()

## Black and White Inlayed Window ##
#window_root = Frame(root,
#			background="black",
#			width=500,
#			height=500)
#window_root.pack()
#window_code = Frame(window_root,

## Inside Center Home ##
#window_code = Frame(root,
#			background="white",
#			width=100,
#			height=100)
#window_code.pack(pady=20,padx=20)

#label_code = Label(window_code, image=img_scan2)
#label_code.pack()

## Read Input Image ##
#img_code = cv2.imread("pics/barcode.png")
#image = opencv_image
#_, frame = cpt.read()
#image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

## Barcode Button ##
#cam_btn = Button(app,
#cam_btn = Button(root,
#		text="Detect Barcode",
#		command=detect_barcode(image))
#cam_btn.pack()

## Show Barcode Button ##
#cam_btn = Button(root,
#		text="Detect Barcode",
#		command=show_barcode(image))
#cam_btn.pack()

#detect_barcode(image)

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

 #       add_btn = tk.Button(top_bar, text="Open Scanner", command=open_camera)
 #       add_btn.pack(side=tk.TOP, padx=10)

        ## Add Calendar ##
 #       cal = DateEntry(top_bar, date_pattern="yyyy-mm-dd")
 #       cal.pack(padx=10, pady=10)

        ## Scrollable Canvas ##
#        if switch_value == True:
#                self.list_canvas = tk.Canvas(self.list_frame, bg="white")
#                self.list_items_frame = tk.Frame(self.list_canvas, bg="white")
#        else:
#                self.list_canvas = tk.Canvas(self.list_frame, bg="#26242f")
#                self.list_items_frame = tk.Frame(self.list_canvas, bg="#26242f")
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

#        add_btn = tk.Button(top_bar, text="Open Scanner", command=open_camera)
#        add_btn.pack(side=tk.TOP, padx=10)

        ## Add Calendar ##
#        cal = DateEntry(top_bar, date_pattern="yyyy-mm-dd")
#        cal.pack(padx=10, pady=10)

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
        self.detail_label = tk.Label(self.detail_frame, text="", font=("Arial", 15), justify="left")
        self.detail_label.pack(pady=30)

        back_btn = tk.Button(self.detail_frame, text="Back", font=("Arial", 15), command=self.back_to_previous_view)
        back_btn.pack(side='bottom', padx=10, pady=10)

    # -------- Popups & Add --------
    def add_item_popup(self):
        name = simpledialog.askstring("Add Item", "Enter Item Name:")
        if not name:
            return

#        expiration_date = simpledialog.askstring("Add Item", "Enter expiration date (YYYY-MM-DD):")
#        expiration_date = selected_date
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
            ## Save Item Input to List or Discard ##
#            try:
#                   with open("items.txt", "w") as out:
#                        out.write('\n'.join(self.items))
#            except:
#                   print ("Unable to Write Data. Discarding...")
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
                command=detect_barcode(img_code))
#                command=detect_barcode(img_scan1))
#                command=show_barcode(detect_barcode))
#                command=detect_barcode(image))
#		comman=open_window_scan)
btn_scan.pack(side='right', padx=10, pady=10)

## Create Light Dark Button ##
btn_mode = Button(root,
               image=lightImg,
#		text="Dark Mode",
#                borderwidth=0,
                background="white",
#		foreground="#26242f",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
		anchor="e",
		cursor="hand2",
                command=toggle)
#btn_mode.pack(side='bottom', padx=10, pady=10)
btn_mode.pack(side='left', padx=10, pady=10)

## Create View Button ##
#switch = Button(window,
btn_view = Button(root,
               image=viewImg,
#		text="View",
#                borderwidth=0,
                background="white",
#		foreground="#26242f",
		foreground="black",
                activebackground="#26242f",
		activeforeground="white",
		anchor="w",
#		sticky="w",
		cursor="hand2",
#                command=show_card_view)
                command=show_barcode(img_code))
#		command=open_window_scan(img_code))
#                command=toggle)
#btn_view.pack(side='bottom', padx=150, pady=10)
btn_view.pack(side='left', padx=10, pady=10)

## Barcode Frame ##
#window_code = Frame(root,
#			background="white",
#			width=100,
#			height=100)
#window_code.pack(pady=20,padx=20)

#label_code = Label(window_code, image=img_scan2)
#label_code.pack()

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
## Import Libraries ##

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
