import customtkinter as ctk
from util.base import Player
import socket
import whisper  # Import OpenAI Whisper
import sounddevice as sd  # For audio recording
import numpy as np  # For handling audio data
import tempfile  # To save temporary audio files
import os  # To manage temporary files
import threading  # To handle recording in a separate thread
import time  # For simulating button hold duration

# Initialize the main app
ctk.set_appearance_mode("System")  # Can be "Light", "Dark", or "System"
ctk.set_default_color_theme("blue")

class PlayerGUI:
    def __init__(self, player_name="Player1"):
        self.player = Player(player_name)
        self.recording = False
        self.connected = True
        self.setup_gui()

    def connect_action(self):
        try:
            self.player.connect()
            self.connected = True
            self.update_game_feed("[System] Connected to server successfully!")
            self.connect_button.configure(text="Disconnect", command=self.disconnect_action)
            self.enable_controls()
        except ConnectionRefusedError:
            self.update_game_feed("[Error] Could not connect to server. Is it running?")
        except socket.error as e:
            self.update_game_feed(f"[Error] Connection failed: {str(e)}")

    def disconnect_action(self):
        try:
            self.player.unjoin()
        except:
            pass
        self.connected = False
        self.connect_button.configure(text="Connect", command=self.connect_action)
        self.disable_controls()
        self.update_game_feed("[System] Disconnected from server")

    def enable_controls(self):
        self.input_textbox.configure(state="normal")
        self.send_button.configure(state="normal")
        self.record_button.configure(state="normal")
        self.tts_toggle.configure(state="normal")

    def disable_controls(self):
        self.input_textbox.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.record_button.configure(state="disabled")
        self.tts_toggle.configure(state="disabled")

    def send_message_action(self):
        if not self.connected:
            return
        message = self.input_textbox.get()
        if message:
            try:
                self.player.take_turn(message)
                self.input_textbox.delete(0, 'end')
                self.game_feed.insert('end', f"[You] -> {message}\n")
            except socket.error as e:
                self.update_game_feed(f"[Error] Failed to send message: {str(e)}")
                self.disconnect_action()

    def update_game_feed(self, message):
        self.game_feed.insert('end', message + '\n')
        self.game_feed.see('end')

    def setup_gui(self):
        self.root = ctk.CTk()
        self.root.title("D&D Player Client")
        self.root.geometry("600x400")
        self.root.minsize(600, 400)
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # ===== Top Frame: Text Box + Toggle Switches =====
        top_frame = ctk.CTkFrame(self.root)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        top_frame.grid_columnconfigure(0, weight=7)
        top_frame.grid_columnconfigure(1, weight=1)
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_rowconfigure(1, weight=1)

        # Game feed using Text widget
        self.game_feed = ctk.CTkTextbox(top_frame, state="disabled")
        self.game_feed.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
        
        # Text to speech toggle
        self.text2speech = ctk.BooleanVar()
        self.tts_toggle = ctk.CTkSwitch(top_frame, text="Text to Speech", variable=self.text2speech)
        self.tts_toggle.grid(row=1, column=1, sticky="ne", padx=10, pady=10)

        # Connection button
        self.connect_button = ctk.CTkButton(top_frame, text="Connect", 
                                          command=self.connect_action)
        self.connect_button.grid(row=0, column=1, sticky="ne", padx=10, pady=10)

        # ===== Bottom Frame: Input Text Box + Buttons =====
        bottom_frame = ctk.CTkFrame(self.root)
        bottom_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        bottom_frame.grid_columnconfigure(0, weight=7)
        bottom_frame.grid_columnconfigure(1, weight=1)
        bottom_frame.grid_rowconfigure(0, weight=1)
        bottom_frame.grid_rowconfigure(1, weight=0, minsize=55)

        # Input text box
        self.input_textbox = ctk.CTkEntry(bottom_frame)
        self.input_textbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)

        # Send message button
        self.send_button = ctk.CTkButton(bottom_frame, text="Send", height=35, 
                                        command=self.send_message_action)
        self.send_button.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")

        # Record button with toggle functionality
        self.record_button = ctk.CTkButton(bottom_frame, text="Record", height=35, 
                                           command=self.toggle_recording)
        self.record_button.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")

        # Initially disable controls until connected
        self.disable_controls()

    def toggle_recording(self):
        """Toggle recording on or off with multithreading."""
        self.recording = not self.recording
        self.record_button.configure(text="RECORDING" if self.recording else "Record")
        
        if self.recording:
            self.start_recording_thread()
        else:
            # Thread will terminate when self.recording becomes False
            pass

    def start_recording_thread(self):
        """Start recording in a separate thread to keep the GUI responsive."""
        self.recording_thread = threading.Thread(target=self.record_audio)
        self.recording_thread.daemon = True  # Make thread terminate when main program exits
        self.recording_thread.start()

    def record_audio(self):
        """Continuously capture audio and process speech-to-text using OpenAI Whisper in a separate thread."""
        try:
            # Load the model once (as a static attribute of the method)
            if not hasattr(self.record_audio, "model"):
                self.update_game_feed("[System] Loading Whisper model...")
                model = whisper.load_model("base")
                
            while self.recording:
                # Record audio
                duration = 5  # seconds
                fs = 16000  # sample rate
                self.update_game_feed("[System] Recording audio...")
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
                sd.wait()  # Wait until recording is finished
                
                # Convert to format expected by Whisper
                audio_data = recording.flatten().astype(np.float32)
                
                # Transcribe
                self.update_game_feed("[System] Transcribing audio...")
                result = model.transcribe(audio_data)
                transcribed_text = result["text"].strip()
                
                if transcribed_text:
                    # Insert the transcribed text into the input textbox
                    self.input_textbox.insert('end', transcribed_text)
                    print(f"Transcribed: {transcribed_text}")
                else:
                    self.update_game_feed("[System] No speech detected")
                
        except Exception as e:
            self.update_game_feed(f"[Error] Recording failed: {str(e)}")
            self.recording = False
            self.record_button.configure(text="Record")

    def start(self):
        """Modified to not auto-connect"""
        try:
            self.root.mainloop()
        finally:
            if self.connected:
                self.disconnect_action()

def main():
    app = PlayerGUI()
    app.start()

if __name__ == "__main__": 
    main()