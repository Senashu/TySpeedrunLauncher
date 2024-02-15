import os
import json
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
import subprocess
import ctypes
from ctypes import wintypes

DEFAULT_ICON = "icon.ico"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
BUTTON_FOLDER = "Buttons"


# Define ctypes structures and constants
class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG),
                ("top", wintypes.LONG),
                ("right", wintypes.LONG),
                ("bottom", wintypes.LONG)]


class WINDOWPLACEMENT(ctypes.Structure):
    _fields_ = [("length", wintypes.UINT),
                ("flags", wintypes.DWORD),
                ("showCmd", wintypes.DWORD),
                ("ptMinPosition", wintypes.POINT),
                ("ptMaxPosition", wintypes.POINT),
                ("rcNormalPosition", RECT)]


GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080

# Load necessary functions from user32.dll
user32 = ctypes.WinDLL('user32')
GetWindowPlacement = user32.GetWindowPlacement
SetWindowLongW = user32.SetWindowLongW
GetWindowLongW = user32.GetWindowLongW


class ProgramLauncher:
    """Class for the program launcher application."""

    def __init__(self, master):
        """Initialize the program launcher."""
        self.master = master
        self.master.iconbitmap(default=DEFAULT_ICON)
        self.master.wm_attributes('-toolwindow', False)  # Set as tool window
        self.master.resizable(False, False)  # Disable resizing
        self.center_window()
        self.load_paths()  # Load paths before creating tabs
        self.create_tabs()
        self.master.after(10, self.show_window)

    # Other methods...

    def show_window(self):
        """Show the window."""
        self.master.attributes("-alpha", 1.0)  # Set window opacity to fully opaque
        self.master.lift()  # Raise the window
        self.master.focus_force()  # Set focus to the window

    def select_program(self, category, program):
        """Select the executable file for the program."""
        selected_file = filedialog.askopenfilename(title=f"Select the executable file for {program}")
        if selected_file:
            self.PROGRAMS[category][program] = selected_file
            with open("settings.json", "w") as json_file:
                json.dump({"PROGRAMS": self.PROGRAMS}, json_file)
            self.launch_program(category, program)

    def center_window(self):
        """Center the window on the screen."""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def create_title_bar(self):
        """Create a draggable title bar."""
        self.title_bar = ctk.CTkFrame(self.master, corner_radius=0)  # No corner radius
        self.title_bar.pack(fill=tk.X)
        self.title_bar.bind("<ButtonPress-1>", self.start_drag)
        self.title_bar.bind("<ButtonRelease-1>", self.stop_drag)
        self.title_bar.bind("<B1-Motion>", self.drag_window)
        self.title_label = ctk.CTkLabel(self.title_bar, text="Ty Speedrun Launcher")
        self.title_label.pack(side=tk.LEFT, padx=5)

    def start_drag(self, event):
        """Start dragging the window."""
        self.x = event.x
        self.y = event.y

    def stop_drag(self, event):
        """Stop dragging the window."""
        self.x = None
        self.y = None

    def drag_window(self, event):
        """Drag the window."""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.master.winfo_x() + deltax
        y = self.master.winfo_y() + deltay
        self.master.geometry(f"+{x}+{y}")

    def create_tabs(self):
        """Create tabs for the launcher application."""
        self.launcher_tab = ctk.CTkFrame(self.master)
        self.launcher_tab.pack(expand=True, fill=ctk.BOTH, padx=5, pady=5)
        self.create_launcher_tab()

    def create_launcher_tab(self):
        """Create the launcher tab."""
        for category, programs in self.PROGRAMS.items():
            frame = ctk.CTkFrame(self.launcher_tab)
            frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True, anchor=tk.N)
            if category:
                ctk.CTkLabel(frame, text=category).pack()
            for program, path in programs.items():
                image_path = os.path.join(BUTTON_FOLDER, f"{program.lower()}.png")
                print("Image Path:", image_path)  # Add this line for debugging
                if os.path.isfile(image_path):
                    image = tk.PhotoImage(file=image_path)
                    button = ctk.CTkButton(frame, image=image, fg_color="transparent", hover=False,
                                           command=lambda c=category, p=program: self.launch_program(c, p))
                    button.image = image
                    # Adjust the size of the button to match the size of the image
                    button.configure(text='', compound=tk.CENTER, width=image.width(), height=image.height())
                    button.pack(pady=5, anchor=tk.N)

    def load_paths(self):
        """Load saved program paths from settings.json or create it with default settings if not found."""
        try:
            with open("settings.json", "r") as json_file:
                self.PROGRAMS = json.load(json_file).get("PROGRAMS", {})
        except FileNotFoundError:
            self.PROGRAMS = {
                "Games": {"Any%": "", "51TE": "", "Mul-Ty-Player Client": "", "Mul-Ty-Player": "", "Any%PM": "",
                          "100%PM": ""},
                "Tools": {"Key2Joy": "", "OutbackMovement": "", "Ty1CollectibleTracker": "",
                          "Mul-Ty-Player Updater": "", "Ty Memory Leak Manager": "",
                          "Tracker": "", "rkvMT": "", "TyPos": ""},
                "Other": {"OBS": "", "VDO Ninja": "", "NohBoard": "", "LiveSplit": ""}
            }
            with open("settings.json", "w") as json_file:
                json.dump({"PROGRAMS": self.PROGRAMS}, json_file)

    def launch_program(self, category, program):
        """Launch the selected program."""
        path = self.PROGRAMS.get(category, {}).get(program)
        if path:
            try:
                program_directory = os.path.dirname(path)  # Get the directory of the program
                if program_directory:
                    os.chdir(program_directory)  # Change the working directory to the program's directory
                    # Launch the program
                    if program == "rkvMT":  # Check if the program is the specific one
                        cmd_command = ['cmd.exe', '/c', 'start', path]
                        subprocess.Popen(cmd_command)
                    else:
                        subprocess.Popen(path)
                else:
                    print(f"Unable to determine the directory for {program}.")
            except Exception as e:
                print(f"An error occurred while launching {program}: {e}")
        else:
            print(f"The path for {program} is empty. Please select the executable file.")
            self.select_program(category, program)  # Prompt user to select the executable file


if __name__ == "__main__":
    root = ctk.CTk()
    root.title("Ty Speedrun Launcher")
    app = ProgramLauncher(root)
    root.mainloop()
