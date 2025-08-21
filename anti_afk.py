"""
AntiAFK - Prevent your PC from going idle by simulating user activity.
Switches focus between open windows to keep status active in Teams, Slack, Zoom, Discord, Skype, and more.
"""


import threading
import time
import random
import pystray
from PIL import Image, ImageDraw
import logging
import pygetwindow as gw
from pywinauto.application import Application

# === CONSTANTS ===
TRAY_ICON_NAME = "AntiAFK"
TRAY_ICON_TITLE = "AntiAFK"
ICON_FILE = "icon.png"
WINDOW_SWITCH_INTERVAL = 120  # seconds
EXCLUDE_TITLE = "AntiAFK"

def create_image():
    """Load tray icon from icon.png, or generate a fallback icon."""
    try:
        logging.info("Loading tray icon from icon.png.")
        return Image.open("icon.png")
    except Exception as e:
        logging.error(f"Error loading icon: {e}")
        image = Image.new('RGB', (64, 64), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.ellipse((16, 16, 48, 48), fill=(0, 0, 0))
        return image

def on_exit(icon, item):
    """Callback for tray icon exit menu."""
    logging.info("Exiting program from tray menu.")
    global running
    running = False
    icon.stop()

def switch_window():
    """Thread function to switch focus between open windows every 2 minutes."""
    logging.info("Window switcher thread started.")
    global running
    while running:
        windows = [w for w in gw.getAllWindows() if w.title and not w.isMinimized]
        logging.info(f"Found {len(windows)} open windows.")
        if len(windows) > 1:
            current = gw.getActiveWindow()
            candidates = [w for w in windows if w != current and 'AntiAFK' not in w.title]
            if not candidates:
                logging.info("No suitable window to switch to.")
            else:
                target = random.choice(candidates)
                logging.info(f"Switching focus to window: {target.title}")
                try:
                    app = Application().connect(handle=target._hWnd)
                    app.top_window().set_focus()
                    logging.info(f"Successfully focused window: {target.title}")
                except Exception as e:
                    logging.error(f"Error focusing window: {e}")
        else:
            logging.info("Not enough windows to switch.")
        for i in range(120):  # 2 minutes
            if not running:
                logging.info("Window switcher thread detected stop signal.")
                break
            if i % 10 == 0:
                logging.info(f"Waiting... {i} seconds elapsed in sleep loop.")
            time.sleep(1)

def main():
    """Main entry point for AntiAFK."""
    global running
    running = True
    # Setup logging to console only
    logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        level=logging.INFO
    )
    logging.info("Starting AntiAFK program.")
    icon = pystray.Icon(
        "AntiAFK",
        create_image(),
        "AntiAFK",
        menu=pystray.Menu(pystray.MenuItem("Exit", on_exit))
    )
    logging.info("Tray icon created. Starting window switcher thread.")
    thread = threading.Thread(target=switch_window, daemon=True)
    thread.start()
    logging.info("Running tray icon event loop.")
    icon.run()
    logging.info("Tray icon event loop exited.")

if __name__ == "__main__":
    main()