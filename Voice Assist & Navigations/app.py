import speech_recognition as sr
import pyttsx3
import webbrowser
import os
import subprocess
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import re  # For regex operations

# Initialize recognizer and TTS engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# List of available commands
AVAILABLE_COMMANDS = [
    "time - Say the current time",
    "open browser - Open the web browser",
    "open calculator - Open the calculator",
    "open youtube - Open YouTube",
    "search google <query> - Search Google",
    "shutdown - Shutdown the system",
    "take a note - Save a voice note",
    "perform <math_expression> - Perform a math operation",
    "exit - Exit the application"
]

# Global flag to control listening
listening = False

def speak(text):
    #Convert text to speech.
    tts_engine.say(text)
    tts_engine.runAndWait()

def take_command():
    #Listen for a voice command and return it as text.
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        display_message("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio).lower()
            display_message(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            speak("Sorry, I didn't catch that.")
            display_message("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError:
            speak("Could not connect to the speech recognition service.")
            display_message("Could not connect to the speech recognition service.")
            return ""
        except sr.WaitTimeoutError:
            display_message("Listening timed out.")
            return ""

def run_command(command):
    #Perform actions based on recognized commands.
    if "time" in command:
        now = datetime.now().strftime("%H:%M")
        speak(f"The time is {now}.")
        display_message(f"The time is {now}.")

    elif "open browser" in command:
        speak("Opening browser.")
        display_message("Opening browser...")
        webbrowser.open("https://www.google.com")

    elif "open calculator" in command:
        speak("Opening calculator.")
        display_message("Opening calculator...")
        if os.name == "nt": #For Windows
            subprocess.Popen("calc.exe")
        elif os.name == "posix": #For MacOS
            subprocess.Popen(["gnome-calculator"])

    elif "open youtube" in command:
        speak("Opening YouTube.")
        display_message("Opening YouTube...")
        webbrowser.open("https://www.youtube.com")

    elif "search google" in command:
        query = command.replace("search google", "").strip()
        speak(f"Searching Google for {query}.")
        display_message(f"Searching Google for: {query}...")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    elif "shutdown" in command:
        speak("Shutting down the system.")
        display_message("Shutting down the system...")
        if os.name == "nt":
            os.system("shutdown /s /t 1")
        elif os.name == "posix":
            os.system("sudo shutdown now")

    elif "take a note" in command:
        speak("What would you like to note down?")
        note = take_command()
        if note:
            with open("notes.txt", "a") as file:
                file.write(f"{note}\n")
            speak("Your note has been saved.")
            display_message("Your note has been saved.")
        else:
            speak("Please specify a valid duration.")
            display_message("Please specify a valid duration.")

    elif "perform" in command:
        expression = command.replace("perform", "").strip()
        try:
            result = eval(expression)
            speak(f"The result is {result}.")
            display_message(f"The result of {expression} is {result}.")
        except Exception as e:
            speak("There was an error performing the calculation.")
            display_message("There was an error performing the calculation.")

    elif "exit" in command:
        speak("Goodbye!")
        display_message("Goodbye!")
        root.quit()  # Exit the GUI

    else:
        speak("I'm not sure how to do that.")
        display_message("I'm not sure how to do that.")

def display_message(message):
    """Display messages and commands in the text area."""
    text_area.insert(tk.END, f"{message}\n")
    text_area.yview(tk.END)  # Auto-scroll to the bottom

def display_available_commands():
    """Display all available commands in the command list area."""
    command_list_area.insert(tk.END, "Available Commands:\n")
    for cmd in AVAILABLE_COMMANDS:
        command_list_area.insert(tk.END, f"- {cmd}\n")
    command_list_area.config(state=tk.DISABLED)  # Make it read-only

def continuous_listen():
    """Continuously listen for commands with pauses between executions."""
    global listening
    while True:
        if listening:
            command = take_command()
            if command:
                run_command(command)
                time.sleep(2)  # Pause for 2 seconds after each command

def toggle_listening():
    """Start or stop the listening process."""
    global listening
    listening = not listening
    if listening:
        speak("Listening started.")
        display_message("Listening started...")
        start_listening_button.config(text="Stop Listening")
    else:
        speak("Listening stopped.")
        display_message("Listening stopped...")
        start_listening_button.config(text="Start Listening")

def start_listening_thread():
    """Start the listening loop in a separate thread."""
    listening_thread = threading.Thread(target=continuous_listen)
    listening_thread.daemon = True  # Ensure thread exits when the main program does
    listening_thread.start()

# Set up the Tkinter GUI
root = tk.Tk()
root.title("Real-Time Voice Assistant")
root.geometry("600x500")

# Text area to display commands and messages
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, width=60)
text_area.pack(pady=10)

# Text area to display available commands (read-only)
command_list_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=6, width=60)
command_list_area.pack(pady=10)

# Button to start/stop listening
start_listening_button = tk.Button(root, text="Start Listening", command=toggle_listening, font=("Arial", 14))
start_listening_button.pack(pady=10)

# Display available commands on startup
display_available_commands()

# Start the assistant with a greeting
speak("How can I help you?")
display_message("How can I help you?")

# Start the continuous listening thread
start_listening_thread()

# Run the GUI main loop
root.mainloop()
