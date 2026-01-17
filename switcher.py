import ctypes
import time
import keyboard
import os
import tempfile

# --- CONFIGURATION ---
CHINESE_SIMPLIFIED_STR = "00000804"
US_ENGLISH_STR = "00000409"

# Windows API Constants
WM_INPUTLANGCHANGEREQUEST = 0x0050

user32 = ctypes.WinDLL('user32', use_last_error=True)

# Logging (Giữ nguyên của bạn để debug)
LOG_FILE = os.path.join(tempfile.gettempdir(), "input_flow_switcher_debug.log")
def log(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {msg}\n")
    except:
        pass

def get_hkl(layout_str):
    """Loads a keyboard layout and returns its handle."""
    return user32.LoadKeyboardLayoutW(layout_str, 1)

def get_current_layout_id():
    """Returns the LID of the current foreground window."""
    foreground_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(foreground_window, None)
    layout_handle = user32.GetKeyboardLayout(thread_id)
    lid = layout_handle & 0xFFFF
    return lid

def switch_to_layout(hkl):
    """Request layout switch safely."""
    foreground_window = user32.GetForegroundWindow()
    log(f"Requesting switch to {hex(hkl)} for window {hex(foreground_window)}")
    
    # 1. Active layout cho thread hiện tại (quan trọng để load layout vào bộ nhớ)
    user32.ActivateKeyboardLayout(hkl, 0)
    
    # 2. Gửi message yêu cầu đổi layout cho cửa sổ đích
    user32.PostMessageW(foreground_window, WM_INPUTLANGCHANGEREQUEST, 0, hkl)

def toggle_unikey():
    log("Toggling Unikey (Ctrl+Shift)")
    keyboard.press_and_release('ctrl+shift')

def switch_kb():
    """
    Logic chuyển đổi thông minh với Verification Loop
    """
    current_lid = get_current_layout_id()
    
    # Xác định mục tiêu
    if current_lid == 0x0409: # Đang là Eng -> Muốn sang Trung
        target_str = CHINESE_SIMPLIFIED_STR
        target_lid_check = 0x0804
        next_state = "Chinese"
    else: # Đang là Trung/Khác -> Muốn về Eng
        target_str = US_ENGLISH_STR
        target_lid_check = 0x0409
        next_state = "English/Vietnamese"

    # 1. Gửi lệnh đổi Layout
    target_hkl = get_hkl(target_str)
    switch_to_layout(target_hkl)
    
    # 2. VÒNG LẶP KIỂM TRA (Trái tim của bản sửa lỗi)
    # Thay vì sleep 0.1s, ta kiểm tra liên tục trong 0.5s xem Layout đã thực sự đổi chưa
    success = False
    for i in range(10): # Thử 10 lần, mỗi lần 0.05s
        time.sleep(0.05) 
        if get_current_layout_id() == target_lid_check:
            success = True
            log(f"Verified layout switch success at attempt {i+1}")
            break
    
    # 3. Quyết định có Toggle Unikey hay không
    if success:
        # Nếu Layout đã đổi thành công -> Mới được phép toggle Unikey
        toggle_unikey()
        return next_state
    else:
        # Nếu Layout KHÔNG đổi (do lỗi quyền, app treo...) -> TUYỆT ĐỐI KHÔNG toggle Unikey
        # Để tránh bị lệch pha (Desync)
        log("Layout switch FAILED or TIMED OUT. Aborting Unikey toggle.")
        return f"Fail: Stuck at {hex(current_lid)}"

if __name__ == "__main__":
    print(f"Current: {hex(get_current_layout_id())}")
