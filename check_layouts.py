import ctypes

def get_keyboard_layouts():
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    
    # Get the number of layouts
    num_layouts = user32.GetKeyboardLayoutList(0, None)
    
    # Get the actual layout handles
    layouts = (ctypes.c_void_p * num_layouts)()
    user32.GetKeyboardLayoutList(num_layouts, layouts)
    
    print(f"Detected {num_layouts} keyboard layouts:")
    for layout in layouts:
        # The lower 16 bits of the layout handle is the LID
        lid = layout & 0xFFFF
        print(f"Handle: {hex(layout)}, LID: {hex(lid)}")

if __name__ == "__main__":
    get_keyboard_layouts()
