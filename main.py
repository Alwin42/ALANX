import customtkinter as ctk
from core.config import BG_COLOR
from ui.auth.login_view import LoginFrame
from workspace_view import WorkspaceFrame

class AlanxApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ALANX - AI Workspace")
        self.geometry("1100x750")
        self.configure(fg_color=BG_COLOR)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None
        self.show_login_screen()

    def show_login_screen(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        self.current_frame = LoginFrame(self, on_login_success=self.show_main_interface)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    def show_main_interface(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        self.current_frame = WorkspaceFrame(self)
        self.current_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = AlanxApp()
    app.mainloop()