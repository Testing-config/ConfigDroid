class Adb_command:
    
    go_back = 'adb shell input keyevent 4'
    
    running_info = r"adb shell dumpsys activity activities | grep Activities="
    
    screen_shot = r"adb shell /system/bin/screencap -p /sdcard/screenshot-{index}.png"
    
    pull_sreen_shot = r"adb pull /sdcard/screenshot-{index}.png {save_path}"
    
    wm_size = "adb shell wm size"