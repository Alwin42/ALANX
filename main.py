import customtkinter as ctk
from database import get_connection

# --- Color Palette ---
BG_COLOR = "#000000"
PURPLE_ACCENT = "#9929EA"
PINK_ACCENT = "#FF5FCF"
YELLOW_TEXT = "#FAEB92"

class AlanxApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("ALANX - AI Workspace")
        self.geometry("1000x700")
        self.configure(fg_color=BG_COLOR)
        
        # Grid Setup for Centering
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Launch Initial Screen
        self.show_login_screen()

    def show_login_screen(self):
        self.login_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        self.login_frame.grid(row=0, column=0, sticky="nsew")
        
        # Center the content vertically and horizontally
        self.login_frame.grid_rowconfigure((0, 5), weight=1)
        self.login_frame.grid_columnconfigure(0, weight=1)
        
        # Title (ALANX)
        title_label = ctk.CTkLabel(
            self.login_frame, 
            text="ALANX", 
            font=("Helvetica", 56, "bold"), 
            text_color=YELLOW_TEXT
        )
        title_label.grid(row=1, column=0, pady=(0, 10))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            self.login_frame, 
            text="Your Intelligent AI Workspace", 
            font=("Helvetica", 18, "bold"), 
            text_color="white"
        )
        subtitle_label.grid(row=2, column=0, pady=(0, 50))
        
        # PIN Entry Container (Mimicking the purple pill from image_9f929f.png)
        self.pin_entry = ctk.CTkEntry(
            self.login_frame, 
            width=280, 
            height=60, 
            corner_radius=30, 
            fg_color=PURPLE_ACCENT, 
            border_width=0, 
            text_color="white", 
            show="●", 
            justify="center", 
            font=("Helvetica", 32, "bold")
        )
        self.pin_entry.grid(row=3, column=0, pady=(0, 30))
        
        # Login Button
        login_btn = ctk.CTkButton(
            self.login_frame, 
            text="LOGIN", 
            font=("Helvetica", 20, "bold"), 
            fg_color="transparent", 
            hover_color="#1A1A1A", 
            text_color="white", 
            command=self.verify_login
        )
        login_btn.grid(row=4, column=0)

    def verify_login(self):
        pin = self.pin_entry.get()
        
        # Database Validation
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE pin=?", (pin,))
            user = cursor.fetchone()
            conn.close()
            
            # Default PIN from Step 1 is "1234"
            if user or pin == "1234": 
                self.login_frame.destroy()
                print("Login Successful! Preparing Main Interface...")
                # self.show_main_interface() <-- We will build this in Step 4
            else:
                # Show error by changing border to Pink Accent
                self.pin_entry.configure(border_width=3, border_color=PINK_ACCENT)
                self.pin_entry.delete(0, 'end')
        except Exception as e:
            print(f"Database error: {e}")

if __name__ == "__main__":
    # Ensure customtkinter matches our scaling needs
    ctk.set_appearance_mode("dark")
    
    app = AlanxApp()
    app.mainloop()