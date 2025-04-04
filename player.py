import customtkinter as ctk
from util.base import Player

# Initialize the main app
ctk.set_appearance_mode("System")  # Can be "Light", "Dark", or "System"
ctk.set_default_color_theme("blue")

def toggle_button_action():
    pass

def send_message_action():
    pass

def main():
    root = ctk.CTk()
    root.title("Enhanced Tkinter App")
    root.geometry("400x250")
    root.minsize(300, 200)
    
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # ===== Top Frame: Text Box + Toggle Switches =====
    top_frame = ctk.CTkFrame(root)
    top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    
    top_frame.grid_columnconfigure(0, weight=2)
    top_frame.grid_columnconfigure(1, weight=1)
    top_frame.grid_rowconfigure(0, weight=1)
    top_frame.grid_rowconfigure(1, weight=1)

    # A text box (Entry) on the left
    game_feed = ctk.CTkEntry(top_frame)
    game_feed.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10), pady=5)
    
    # Two toggle switches (Switches in customtkinter)
    text2Speech: bool = ctk.BooleanVar()

    ttsToggle = ctk.CTkSwitch(top_frame, text="Text to Speech", variable=text2Speech)

    ttsToggle.grid(row=1, column=1, sticky="w")

    # ===== Bottom Frame: Input Text Box + Buttons =====
    bottom_frame = ctk.CTkFrame(root)
    bottom_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    
    bottom_frame.grid_columnconfigure(0, weight=2)
    bottom_frame.grid_columnconfigure(1, weight=1)
    bottom_frame.grid_rowconfigure(0, weight=1)
    bottom_frame.grid_rowconfigure(1, weight=1)

    # Second text box
    InputTextBox = ctk.CTkEntry(bottom_frame)
    InputTextBox.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

    # A toggle button to the right of the second text box
    Recording_var = ctk.BooleanVar(value=False)

    def toggle_button_action():
        Recording_var.set(not Recording_var.get())
        RecordButton.configure(text="Record" if Recording_var.get() else "RECORDING")

    RecordButton = ctk.CTkButton(bottom_frame, text="Record", command=toggle_button_action)
    RecordButton.grid(row=0, column=1, padx=5, sticky="nsew")

    # Another larger button below
    SendMessageButton = ctk.CTkButton(bottom_frame, text="Send", height=35, command=send_message_action)
    SendMessageButton.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="nsew")

    root.mainloop()

if __name__ == "__main__":
    main()