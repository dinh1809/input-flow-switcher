import os
import sys
import threading
import keyboard
import pystray
from PIL import Image, ImageDraw
from win10toast import ToastNotifier
import switcher

import winreg

# Notification system
toaster = ToastNotifier()
APP_NAME = "InputFlowSwitcher"

def create_image(color1, color2):
    # Generate an icon for the tray
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle([width//2, 0, width, height], fill=color2)
    return image

def notify_change(state_name):
    """Shows a toast notification."""
    # Using a thread to avoid blocking the main UI
    def show():
        toaster.show_toast(
            "Keyboard Switched",
            f"Now using: {state_name}",
            duration=2,
            threaded=True
        )
    threading.Thread(target=show).start()

def on_toggle():
    """Triggered by the hotkey."""
    try:
        new_state = switcher.switch_kb()
        notify_change(new_state)
    except Exception as e:
        print(f"Error switching: {e}")

def is_startup_enabled():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except WindowsError:
        return False

def toggle_startup(icon, item):
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE | winreg.KEY_READ)
    if is_startup_enabled():
        winreg.DeleteValue(key, APP_NAME)
    else:
        # If running from script, this might be python.exe main.py, but for EXE it's the exe path
        exe_path = os.path.realpath(sys.executable if getattr(sys, 'frozen', False) else sys.argv[0])
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, exe_path)
    winreg.CloseKey(key)

def exit_action(icon, item):
    icon.stop()
    os._exit(0)

def setup_tray():
    # Setup the system tray icon
    image = create_image("blue", "red")
    menu = pystray.Menu(
        pystray.MenuItem("Toggle (Alt+Z)", on_toggle),
        pystray.MenuItem("Run at Startup", toggle_startup, checked=lambda item: is_startup_enabled()),
        pystray.MenuItem("Exit", exit_action)
    )
    icon = pystray.Icon("KB Switcher", image, "Input Flow Switcher", menu)
    
    # Register global hotkey
    keyboard.add_hotkey('alt+z', on_toggle)
    
    print("Application running... Press Alt+Z to switch layout.")
    icon.run()

if __name__ == "__main__":
    setup_tray()
