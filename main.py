import ctypes
import os
import sys
import threading
import time
import winreg

import requests
from tkinter import *
from PIL import Image, ImageTk
from idlelib.tooltip import Hovertip
import pystray
from pystray import Icon as Icon, MenuItem as MenuItem
import darkdetect

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        # If running in a PyInstaller bundle
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

REQUEST_TIMEOUT = 5
IMG_DIR = resource_path("img")
PIRATE_FLAG = f"{IMG_DIR}/pirate_flag.png"

class Application:
    def __init__(self):
        self.stop_program = False
        self.state = 0
        self.last_ip = None

        self.root = Tk()

        self.root.title("MyIP Widget")
        self.root.iconbitmap(f"{IMG_DIR}\\icon.ico")

        self.detect_theme()

        self.lab1 = Label(self.root, bg=self.bg_color)
        self.lab1.bind("<Button-3>", self.hide_window)
        self.lab2 = Label(self.root, bd=0, bg=self.bg_color, fg=self.fg_color, highlightthickness=0, borderwidth=0)
        self.lab3 = Label(self.root, bd=0, bg=self.bg_color, fg=self.fg_color, highlightthickness=0, borderwidth=0)

        self.lab1.grid(row=1, column=1)
        self.lab2.grid(row=2, column=1)
        self.lab3.grid(row=3, column=1)

        Hovertip(self.lab1, 'right click to close')

        self.icon = pystray.Icon("ping")
        self.icon.icon = Image.open(PIRATE_FLAG)
        self.icon.run_detached()
        self.icon.menu = (
            MenuItem('Quit', lambda: self.quit_window()),
            MenuItem('Show', self.show_window)
        )
        # self.root.wm_attributes("-transparentcolor", self.bg_color)
        self.root.overrideredirect(True)
        self.root.attributes("-alpha", 0.7)
        self.root.attributes('-topmost', True)
        self.root.configure(bg=self.bg_color)
        self.root.bind("<B1-Motion>", self.move_window)

        self.thread2 = threading.Thread(target=self.update_data)
        self.thread2.start()

    def detect_theme(self):
        theme = darkdetect.theme()

        if theme == "Dark":
            self.bg_color = "black"
            self.fg_color = "white"
        else:
            self.bg_color = "white"
            self.fg_color = "black"

    def move_window(self, event):
        self.root.geometry(f'+{event.x_root}+{event.y_root}')

    def quit_window(self):
        self.stop_program = True
        self.icon.icon = None
        self.icon.title = None
        self.icon.stop()
        self.root.destroy()

    def show_window(self):
        self.root.after(0, self.root.deiconify())

    def hide_window(self, event):
        self.root.withdraw()

    def find_ip(self):
        try:
            req = requests.get("http://ip-api.com/json/", timeout=REQUEST_TIMEOUT)
            if req.status_code == 200:
                ip_data = req.json()
                return ip_data
            else:
                return False
        except Exception as e:
            print(e)
            return False

    def update_data(self):
        while not self.stop_program:
            ip = self.find_ip()
            if ip:
                ip_address = ip["query"]
                if ip_address != self.last_ip:
                    self.last_ip = ip_address
                    self.lab1.image = ImageTk.PhotoImage(image=Image.open(f"{IMG_DIR}\\flags\\{ip['countryCode']}.png"))
                    self.lab1.config(image=self.lab1.image)
                    self.lab2.config(text=ip["country"])
                    self.lab3.config(text=ip_address)
                    self.icon.icon = Image.open(f"{IMG_DIR}\\flags\\{ip['countryCode']}.png")
                    self.icon.title = ip_address
            else:
                self.last_ip = None
                self.lab1.image = ImageTk.PhotoImage(file=PIRATE_FLAG)
                self.lab1.config(image=self.lab1.image)
                self.lab2.config(text="No Internet")
                self.lab3.config(text="")
                self.icon.icon = Image.open(PIRATE_FLAG)
            time.sleep(5)

    def run(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # if your windows version >= 8.1
        except:
            ctypes.windll.user32.SetProcessDPIAware()  # win 8.0 or less

        self.root.mainloop()
        os._exit(1)


if __name__ == '__main__':
    app = Application()
    app.run()
