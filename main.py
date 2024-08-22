import tkinter as tk
from tkinter import ttk
import time
import pyttsx3
import subprocess
import threading
import ctypes
import win32gui
import win32com.client
import win32con

# Initialize flags
timer_running = False
restart_requested = False

def speak(text, rate=200):  # Change the rate of speech
    
    engine = pyttsx3.init()
    
    # Set the speech rate
    engine.setProperty('rate', rate)
    
    engine.say(text)
    engine.runAndWait()

def play_song():
    ahk_script_path = r'open_spotify.ahk'
    ahk_executable = r'C:\Program Files\AutoHotkey\UX\AutoHotkeyUX.exe'
    subprocess.run([ahk_executable, ahk_script_path], check=True)

def stop_playback():
    ahk_stop_script = r'stop_spotify.ahk'
    ahk_executable = r'C:\Program Files\AutoHotkey\UX\AutoHotkeyUX.exe'
    subprocess.run([ahk_executable, ahk_stop_script], check=True)

def validate_input():
    work_time = work_time_entry.get().strip()
    break_time = break_time_entry.get().strip()
    
    if not work_time or not break_time:
        speak("Please enter values for both work time and break time.")
        return False
    
    if not work_time.isdigit() or not break_time.isdigit():
        speak("Please enter only numbers for work time and break time.")
        return False
    
    return True

def start_timer():
    global timer_running, restart_requested, repeat_active
    if not timer_running:
        if not validate_input():
            return
        
        work_time = int(work_time_entry.get()) * 60
        break_time = int(break_time_entry.get()) * 60
        timer_running = True
        restart_requested = False
        repeat_active = False
        start_button.config(text="Restart")
        threading.Thread(target=countdown, args=(work_time, break_time), daemon=True).start()

def restart_timer():
    global restart_requested, timer_running, repeat_active
    restart_requested = True
    timer_running = False
    repeat_active = False
    stop_all_processes()
    reset_application_state()

def stop_all_processes():
    global timer_running, repeat_active
    timer_running = False
    repeat_active = False
    root.after_cancel(repeat_message)  # Cancel any scheduled repeat_message calls

def reset_application_state():
    global session_count
    
    update_session_counter()
    timer_var.set("Timer")
    start_button.config(text="Start Timer")
    root.unbind('<Key>')

def countdown(work_time, break_time):
    global timer_running, restart_requested
    while work_time and not restart_requested:
        mins, secs = divmod(work_time, 60)
        root.after(0, timer_var.set, f'Work Time: {mins:02d}:{secs:02d}')
        time.sleep(1)
        work_time -= 1
        if restart_requested:
            return

    if not restart_requested:
        speak("Great Job !. You've completed your study time. Now you can take a break. let me play some music for you")
        play_song()

        while break_time and not restart_requested:
            mins, secs = divmod(break_time, 60)
            root.after(0, timer_var.set, f'Break Time: {mins:02d}:{secs:02d}')
            time.sleep(1)
            break_time -= 1
            if restart_requested:
                return
            
        stop_playback()
        time.sleep(1)
        
        if not restart_requested:
            root.after(0, bring_window_to_front)
            global session_count
            session_count += 1
            root.after(0, update_session_counter)
            root.after(0, wait_for_key_press)
    
    timer_running = False
    if restart_requested:
        root.after(0, start_timer)  # Schedule start_timer to run in the main thread

def wait_for_key_press():
    global repeat_active
    repeat_active = True
    root.after(0, timer_var.set, "Press any key to start working")
    root.bind('<Key>', on_key_press)
    
    repeat_message()

def bring_window_to_front():
    hwnd = win32gui.FindWindow(None, "Smart Timer Application")
    
    if hwnd:
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        win32gui.SetForegroundWindow(hwnd)
        win32gui.BringWindowToTop(hwnd)
        win32gui.SetActiveWindow(hwnd)
    else:
        print("Window not found!")

def repeat_message():
    global repeat_active
    if repeat_active and not restart_requested:
        
        speak("Break time is over. Back to work")
        root.after(2000, repeat_message)

def on_key_press(event):
    global repeat_active
    repeat_active = False
    root.unbind('<Key>')
    start_timer()

def update_session_counter():
    session_counter_var.set(f"Sessions Completed: {session_count}")

# Setting up the Tkinter window
root = tk.Tk()
root.title("Smart Timer Application")
root.geometry("400x400")
root.configure(bg="#f0f0f0")

style = ttk.Style()
style.theme_use('clam')

# Configure styles
style.configure("TLabel", font=("Helvetica", 12), background="#f0f0f0")
style.configure("TButton", font=("Helvetica", 12), padding=10)
style.configure("TEntry", font=("Helvetica", 12), padding=5)

timer_var = tk.StringVar()
timer_var.set("Timer")

session_counter_var = tk.StringVar()
session_count = 0
update_session_counter()

# Main frame
main_frame = ttk.Frame(root, padding="20 20 20 20", style="Main.TFrame")
main_frame.pack(fill=tk.BOTH, expand=True)

# Timer display
timer_label = ttk.Label(main_frame, textvariable=timer_var, font=("Helvetica", 28), background="#f0f0f0")
timer_label.pack(pady=20)

# Input frame
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=tk.X, pady=10)

ttk.Label(input_frame, text="Work Time (min):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
work_time_entry = ttk.Entry(input_frame, width=10)
work_time_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(input_frame, text="Break Time (min):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
break_time_entry = ttk.Entry(input_frame, width=10)
break_time_entry.grid(row=1, column=1, padx=5, pady=5)

# Session counter
session_label = ttk.Label(main_frame, textvariable=session_counter_var, font=("Helvetica", 16), background="#f0f0f0")
session_label.pack(pady=10)

# Start/Restart Button
start_button = ttk.Button(main_frame, text="Start Timer", command=lambda: start_timer() if not timer_running else restart_timer())
start_button.pack(pady=20)

repeat_active = False

root.mainloop()