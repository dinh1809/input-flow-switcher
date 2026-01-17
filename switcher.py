import ctypes
import time
import keyboard

# Keyboard Layout strings
CHINESE_SIMPLIFIED_STR = "00000804"
US_ENGLISH_STR = "00000409"

# Windows API Constants
WM_INPUTLANGCHANGEREQUEST = 0x0050
HWND_BROADCAST = 0xFFFF

user32 = ctypes.WinDLL('user32', use_last_error=True)

def get_hkl(layout_str):
    """Loads a keyboard layout and returns its handle."""
    return user32.LoadKeyboardLayoutW(layout_str, 1)

import os
import tempfile

# Set up simple logging in TEMP directory
LOG_FILE = os.path.join(tempfile.gettempdir(), "input_flow_switcher_debug.log")

def log(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    except:
        pass

def get_current_layout_id():
    """Returns the LID of the current foreground window's keyboard layout."""
    foreground_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(foreground_window, None)
    layout_handle = user32.GetKeyboardLayout(thread_id)
    lid = layout_handle & 0xFFFF
    log(f"Foreground Window: {hex(foreground_window)}, Thread ID: {thread_id}, HKL: {hex(layout_handle)}, LID: {hex(lid)}")
    return lid

def switch_to_layout(hkl):
    """
    Switches the keyboard layout for the current thread and sends a message
    to the foreground window.
    """
    foreground_window = user32.GetForegroundWindow()
    log(f"Requesting layout switch to {hex(hkl)} for window {hex(foreground_window)}")
    
    # 1. Activate layout for the current thread (the app itself)
    # This sometimes helps the system sync better
    user32.ActivateKeyboardLayout(hkl, 0)
    
    # 2. PostMessage to foreground window
    # WM_INPUTLANGCHANGEREQUEST: wParam=0, lParam=hkl
    user32.PostMessageW(foreground_window, WM_INPUTLANGCHANGEREQUEST, 0, hkl)
    
    # 3. Try to broadcast it to ensure the taskbar updates
    # user32.PostMessageW(HWND_BROADCAST, WM_INPUTLANGCHANGEREQUEST, 0, hkl)

def toggle_unikey():
    """Simulates Ctrl + Shift to toggle Unikey state."""
    log("Toggling Unikey (Ctrl+Shift)")
    keyboard.press_and_release('ctrl+shift')

def switch_kb():
    """
    Main toggle function.
    """
    current_lid = get_current_layout_id()
    
    if current_lid == 0x0409:
        # Switch to Chinese (Simplified)
        hkl = get_hkl(CHINESE_SIMPLIFIED_STR)
        switch_to_layout(hkl)
        time.sleep(0.1)
        toggle_unikey()
        return "Chinese"
    else:
        # Switch to English (US)
        hkl = get_hkl(US_ENGLISH_STR)
        switch_to_layout(hkl)
        time.sleep(0.1)
        toggle_unikey()
        return "English/Vietnamese"

if __name__ == "__main__":
    print(f"Current layout LID: {hex(get_current_layout_id())}")
    # Testing toggle
    # new_state = switch_kb()
    # print(f"Switched to: {new_state}")
