import customtkinter as ctk

# Initialize the main app
ctk.set_appearance_mode("System")  # Can be "Light", "Dark", or "System"
ctk.set_default_color_theme("blue")

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
    text_box_1 = ctk.CTkEntry(top_frame)
    text_box_1.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(0, 10), pady=5)
    
    # Two toggle switches (Switches in customtkinter)
    toggle_var1 = ctk.BooleanVar()
    toggle_var2 = ctk.BooleanVar()

    toggle1 = ctk.CTkSwitch(top_frame, text="Toggle 1", variable=toggle_var1)
    toggle2 = ctk.CTkSwitch(top_frame, text="Toggle 2", variable=toggle_var2)

    toggle1.grid(row=0, column=1, sticky="w", pady=5)
    toggle2.grid(row=1, column=1, sticky="w")

    # ===== Bottom Frame: Input Text Box + Buttons =====
    bottom_frame = ctk.CTkFrame(root)
    bottom_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    
    bottom_frame.grid_columnconfigure(0, weight=2)
    bottom_frame.grid_columnconfigure(1, weight=1)
    bottom_frame.grid_rowconfigure(0, weight=1)
    bottom_frame.grid_rowconfigure(1, weight=1)

    # Second text box
    text_box_2 = ctk.CTkEntry(bottom_frame)
    text_box_2.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)

    # A button to the right of the second text box
    button_1 = ctk.CTkButton(bottom_frame, text="Button")
    button_1.grid(row=0, column=1, padx=5, sticky="nsew")

    # Another larger button below
    button_2 = ctk.CTkButton(bottom_frame, text="Big Button", height=35)
    button_2.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="nsew")

    root.mainloop()

if __name__ == "__main__":
    main()