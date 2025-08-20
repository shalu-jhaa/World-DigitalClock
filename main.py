import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps, ImageChops, Image
from datetime import datetime
import pytz
import os

# Country list with timezone
COUNTRIES = {
    "India": "Asia/Kolkata",
    "USA": "America/New_York",
    "UK": "Europe/London",
    "Japan": "Asia/Tokyo",
    "China": "Asia/Shanghai",
    "Australia": "Australia/Sydney",
    "Germany": "Europe/Berlin",
    "France": "Europe/Paris",
    "Russia": "Europe/Moscow",
    "Brazil": "America/Sao_Paulo",
    "Canada": "America/Toronto",
    "South Africa": "Africa/Johannesburg",
    "UAE": "Asia/Dubai",
    "Singapore": "Asia/Singapore",
    "Italy": "Europe/Rome",
    "Spain": "Europe/Madrid",
    "Mexico": "America/Mexico_City",
    "South Korea": "Asia/Seoul",
    "Saudi Arabia": "Asia/Riyadh",
    "Egypt": "Africa/Cairo",
}

# Resolve script directory and images folder (works no matter where you run it from)
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()

IMAGE_FOLDER = os.path.join(SCRIPT_DIR, "images")
ALLOWED_EXTS = (".jpg", ".jpeg", ".png", ".webp")

CANVAS_W, CANVAS_H = 800, 450


class WorldClockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌍 World Digital Clock")
        self.root.geometry("800x500")
        self.root.resizable(False, False)

        # top bar
        top = tk.Frame(root, bg="black")
        top.pack(fill="x")

        tk.Label(top, text="Select Country:", font=("Arial", 14), fg="white", bg="black").pack(side="left", padx=10)

        self.country_var = tk.StringVar()
        self.country_dropdown = ttk.Combobox(top, textvariable=self.country_var, values=list(COUNTRIES.keys()), font=("Arial", 12), state="readonly", width=18)
        self.country_dropdown.current(0)
        self.country_dropdown.pack(side="left", padx=10)
        self.country_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_country())

        ttk.Button(top, text="Show Time", command=self.update_country).pack(side="left", padx=10)

        # status label (tells which image loaded / fallback)
        self.status_var = tk.StringVar(value="")
        tk.Label(top, textvariable=self.status_var, font=("Arial", 10), fg="white", bg="black").pack(side="right", padx=10)

        # canvas
        self.canvas = tk.Canvas(root, width=CANVAS_W, height=CANVAS_H, highlightthickness=0)
        self.canvas.pack()

        # Create persistent canvas items (one background image + two texts)
        self.bg_photo = None  # keep reference so it isn't garbage-collected
        self.bg_item = self.canvas.create_image(0, 0, anchor="nw")  # will set image later

        self.time_item = self.canvas.create_text(CANVAS_W // 2, CANVAS_H - 100, text="", fill="white",
                                                 font=("Arial", 32, "bold"))
        self.country_item = self.canvas.create_text(CANVAS_W // 2, CANVAS_H - 50, text="", fill="yellow",
                                                    font=("Arial", 20, "bold"))

        # simple cache so we don't re-open the same image repeatedly
        self._image_cache = {}

        # initial draw
        self.update_country()
        self.update_time()

    # -------- helper methods --------
    def _country_to_basename(self, country: str) -> str:
        # normalize names to filenames (e.g., "South Africa" -> "south_africa")
        return country.strip().lower().replace(" ", "_")

    def _find_image_path(self, country: str):
        """
        Try to find an image for the country in images folder with any allowed extension.
        Returns a path or None.
        """
        base = self._country_to_basename(country)
        for ext in ALLOWED_EXTS:
            candidate = os.path.join(IMAGE_FOLDER, base + ext)
            if os.path.exists(candidate):
                return candidate
        return None

    def _load_background(self, country: str):
        """
        Load and fit background to canvas size.
        If not found, return a solid black image.
        """
        key = (country, CANVAS_W, CANVAS_H)
        if key in self._image_cache:
            return self._image_cache[key]

        img_path = self._find_image_path(country)
        if img_path:
            try:
                img = Image.open(img_path)
                # Fit while preserving aspect ratio; crop center if needed
                fitted = ImageOps.fit(img, (CANVAS_W, CANVAS_H), method=Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(fitted)
                self._image_cache[key] = photo
                self.status_var.set(f"Background: {os.path.basename(img_path)}")
                return photo
            except Exception as e:
                self.status_var.set(f"Image error: {e}. Using solid background.")

        # fallback: solid black
        fallback = Image.new("RGB", (CANVAS_W, CANVAS_H), "black")
        photo = ImageTk.PhotoImage(fallback)
        self._image_cache[key] = photo
        if not img_path:
            self.status_var.set("Background: none (solid black)")
        return photo

    # -------- UI updates --------
    def update_country(self):
        country = self.country_var.get() or list(COUNTRIES.keys())[0]
        # Set background
        self.bg_photo = self._load_background(country)
        self.canvas.itemconfig(self.bg_item, image=self.bg_photo)

        # Set country label
        self.canvas.itemconfig(self.country_item, text=country)

    def update_time(self):
        country = self.country_var.get() or list(COUNTRIES.keys())[0]
        tz = pytz.timezone(COUNTRIES[country])
        current_time = datetime.now(tz).strftime("%H:%M:%S")
        self.canvas.itemconfig(self.time_item, text=current_time)

        # schedule next tick
        self.root.after(1000, self.update_time)


if __name__ == "__main__":
    root = tk.Tk()
    app = WorldClockApp(root)
    root.mainloop()

