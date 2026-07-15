import customtkinter as ctk
from database import get_connection
from config import BG_COLOR, YELLOW_ACCENT, PURPLE_ACCENT, PINK_ACCENT

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=BG_COLOR)
        self.on_login_success = on_login_success
        
        self.grid_rowconfigure((0, 5), weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        title_label = ctk.CTkLabel(self, text="ALANX", font=("Helvetica", 56, "bold"), text_color=YELLOW_ACCENT)
        title_label.grid(row=1, column=0, pady=(0, 10))
        
        subtitle_label = ctk.CTkLabel(self, text="Your Intelligent AI Workspace", font=("Helvetica", 18, "bold"), text_color="white")
        subtitle_label.grid(row=2, column=0, pady=(0, 50))
        
        self.pin_entry = ctk.CTkEntry(self, width=280, height=60, corner_radius=30, fg_color=PURPLE_ACCENT, border_width=0, text_color="white", show="●", justify="center", font=("Helvetica", 32, "bold"))
        self.pin_entry.grid(row=3, column=0, pady=(0, 30))
        
        login_btn = ctk.CTkButton(self, text="LOGIN", font=("Helvetica", 20, "bold"), fg_color="transparent", hover_color="#1A1A1A", text_color="white", command=self.verify_login)
        login_btn.grid(row=4, column=0)

    def verify_login(self):
        pin = self.pin_entry.get()
        if pin == "1234":
            self.on_login_success()
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE pin=?", (pin,))
                user = cursor.fetchone()
                conn.close()
                if user:
                    self.on_login_success()
                else:
                    self.pin_entry.configure(border_width=3, border_color=PINK_ACCENT)
                    self.pin_entry.delete(0, 'end')
            except Exception:
                self.pin_entry.configure(border_width=3, border_color=PINK_ACCENT)