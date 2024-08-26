import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

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
total_study_time = 0

def speak(text, rate=200):
    engine = pyttsx3.init()
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()

def play_song():
    ahk_script_path = r'open_spotify.exe' #change the file path 
    subprocess.run([ahk_script_path], check=True)

def stop_playback():
    ahk_stop_script = r'stop_spotify.exe' #change the file path
    subprocess.run([ahk_stop_script], check=True)

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
    global timer_running, restart_requested, repeat_active, total_study_time
    if not timer_running:
        if not validate_input():
            return
        
        work_time = int(work_time_entry.get()) * 60  # Convert to seconds
        break_time = int(break_time_entry.get()) * 60  # Convert to seconds
        timer_running = True
        restart_requested = False
        repeat_active = False
        start_button.configure(text="Restart")
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
    start_button.configure(text="Start Timer")
    root.unbind('<Key>')

def countdown(work_time, break_time):
    global timer_running, restart_requested, total_study_time
    initial_work_time = work_time
    while work_time and not restart_requested:
        mins, secs = divmod(work_time, 60)
        root.after(0, timer_var.set, f'Work Time: {mins:02d}:{secs:02d}')
        time.sleep(1)
        work_time -= 1
        if restart_requested:
            return

    if not restart_requested:
        total_study_time += initial_work_time
        root.after(0, update_progress_bar)
        speak("Great Job! You've completed your study time. Now you can take a break. Let me play some music for you")
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

def update_progress_bar():
    try:
        goal_seconds = float(goal_entry.get()) * 360 # Convert hours to seconds
        progress = (total_study_time / goal_seconds) * 100
        progress_bar.set(progress / 100)  # Set expects a value between 0 and 1
        
        completed_time = min(total_study_time, goal_seconds)
        hours_completed, remainder = divmod(completed_time, 3600)
        minutes_completed, _ = divmod(remainder, 60)
        
        progress_label.configure(text=f"Completed: {int(hours_completed)}h {int(minutes_completed)}m")
        
        if total_study_time < goal_seconds:
            root.after(1000, update_progress_bar)  # Call update_progress_bar every second
        else:
            speak("Congratulations! You have achieved your goal for today. Setup New goal or enjoy the achievement")
            restart_timer()
    except ValueError:
        speak("Please enter a valid number for the daily goal.")

def reset_progress():
    global total_study_time
    total_study_time = 0
    update_progress_bar()

def wait_for_key_press():
    global repeat_active
    repeat_active = True
    root.after(0, timer_var.set, "Press any key to start working")
    root.bind('<Key>', on_key_press)
    
    repeat_message()

def bring_window_to_front():
    hwnd = win32gui.FindWindow(None, "Talking Timer")
    
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

# Set up the custom theme (optional)
ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (default), "green", "dark-blue"

# Setting up the customtkinter window
root = ctk.CTk()  # Use CTk instead of tk.Tk()
root.title("Talking Timer")
root.geometry("435x475")  # Increased height to accommodate new elements

timer_var = tk.StringVar()
timer_var.set("Timer")

session_counter_var = tk.StringVar()
session_count = 0
update_session_counter()

# Main scrollable frame
main_frame = ctk.CTkScrollableFrame(root, corner_radius=10, scrollbar_button_color="#2CC985", scrollbar_button_hover_color="#2FA572")
main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

# Adjust scrollbar width
main_frame._scrollbar.configure(width=10)

# Timer section
timer_section = ctk.CTkFrame(main_frame, corner_radius=10)
timer_section.pack(fill=tk.X, pady=(0, 20))

# Timer display
timer_label = ctk.CTkLabel(timer_section, textvariable=timer_var, font=("Helvetica", 28))
timer_label.pack(pady=20)

# Input frame
input_frame = ctk.CTkFrame(timer_section)
input_frame.pack(fill=tk.X, pady=10)

ctk.CTkLabel(input_frame, text="Work Time (min):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
work_time_entry = ctk.CTkEntry(input_frame, width=100)
work_time_entry.grid(row=0, column=1, padx=5, pady=5)
work_time_entry.insert(0, "25") 

ctk.CTkLabel(input_frame, text="Break Time (min):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
break_time_entry = ctk.CTkEntry(input_frame, width=100)
break_time_entry.grid(row=1, column=1, padx=5, pady=5)
break_time_entry.insert(0, "5")

# Daily Goal input
ctk.CTkLabel(input_frame, text="Daily Goal (hours):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
goal_entry = ctk.CTkEntry(input_frame, width=100)
goal_entry.grid(row=2, column=1, padx=5, pady=5)
goal_entry.insert(0, "5")  # Default 5 hours

# Progress bar
progress_bar = ctk.CTkProgressBar(timer_section, width=300)
progress_bar.pack(pady=10)
progress_bar.set(0)

progress_label = ctk.CTkLabel(timer_section, text="Time left: 0h 0m", font=("Helvetica", 16))
progress_label.pack(pady=5)

# Session counter
session_label = ctk.CTkLabel(timer_section, textvariable=session_counter_var, font=("Helvetica", 16))
session_label.pack(pady=10)

# Start/Restart Button
start_button = ctk.CTkButton(timer_section, text="Start Timer", command=lambda: start_timer() if not timer_running else restart_timer())
start_button.pack(pady=20)

spacer_frame = ctk.CTkFrame(main_frame, height=18, corner_radius=7 , fg_color="#D3D3D3")  # Adjust height as needed
spacer_frame.pack(fill=tk.X, pady=(0, 10))

# Task section
task_section = ctk.CTkFrame(main_frame, corner_radius=10)
task_section.pack(fill=tk.X, pady=(0, 20))

ctk.CTkLabel(task_section, text="Tasks", font=("Helvetica", 25)).pack(pady=10)

# Frame to hold all tasks
task_list_frame = ctk.CTkFrame(task_section)
task_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Task input and add button frame
input_frame = ctk.CTkFrame(task_section)
input_frame.pack(fill=tk.X, padx=10, pady=10)

task_input = ctk.CTkEntry(input_frame, width=250)
task_input.pack(side=tk.LEFT, padx=(0, 5))

def add_task():
    task = task_input.get()
    if task:
        task_frame = ctk.CTkFrame(task_list_frame)
        task_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Left section for checkbox
        left_section = ctk.CTkFrame(task_frame)
        left_section.pack(side=tk.LEFT, padx=(0, 0), fill=tk.Y)
        
        var = tk.IntVar()
        cb = ctk.CTkCheckBox(left_section, text="", variable=var, width= 0,
                             command=lambda: task_label.configure(font=("Helvetica", 12, "overstrike" if var.get() else "normal")))
        cb.pack(expand=True)
        
        # Right section for text and delete button
        right_section = ctk.CTkFrame(task_frame)
        right_section.pack(side=tk.LEFT, padx=(0, 0), fill=tk.BOTH, expand=True)
        
        task_label = ctk.CTkLabel(right_section, text=task, anchor="w", justify="left")
        task_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        delete_btn = ctk.CTkButton(right_section, text="Delete", width=60, 
                                   command=lambda: task_frame.destroy())
        delete_btn.pack(side=tk.RIGHT, padx=(5, 2))
        
        task_input.delete(0, tk.END)

add_task_btn = ctk.CTkButton(input_frame, text="Add Task", width=100, command=add_task)
add_task_btn.pack(side=tk.LEFT)
repeat_active = False
update_progress_bar()

root.mainloop()