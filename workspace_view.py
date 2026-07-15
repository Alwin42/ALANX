import threading
import customtkinter as ctk
from config import BG_COLOR, INNER_CONTAINER_BG, PURPLE_ACCENT, YELLOW_ACCENT
from api_client import get_ai_response

class WorkspaceFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BG_COLOR)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=5)
        
        # Model mapping: "UI Display Name": ("API Model ID", "provider")
        self.MODEL_MAP = {
            "OpenRouter: Poolside Laguna M.1": ("poolside/laguna-m.1", "openrouter"),
            "OpenRouter: Qwen 3 Coder (Free)": ("qwen/qwen3-coder:free", "openrouter"),
            "OpenRouter: GPT-OSS 20B (Free)": ("openai/gpt-oss-20b:free", "openrouter"),
            "Nvidia: Meta Llama 3 70B": ("meta/llama3-70b-instruct", "nvidia"),
            "Nvidia: Mixtral 8x22B": ("mistralai/mixtral-8x22b-instruct-v0.1", "nvidia")
        }
        
        self._build_sidebar()
        self._build_chat_area()

    def _build_sidebar(self):
        sidebar_frame = ctk.CTkFrame(self, fg_color=BG_COLOR)
        sidebar_frame.grid(row=0, column=0, sticky="nsw", padx=(0, 20), pady=20)
        sidebar_frame.grid_rowconfigure((0, 4), weight=1)
        
        nav_font = ("Helvetica", 20, "bold")
        
        ctk.CTkButton(sidebar_frame, text="History", font=nav_font, fg_color="transparent", text_color="white", anchor="w", hover_color="#1A1A1A").grid(row=1, column=0, pady=15, sticky="w")
        ctk.CTkButton(sidebar_frame, text="Profile", font=nav_font, fg_color="transparent", text_color="white", anchor="w", hover_color="#1A1A1A").grid(row=2, column=0, pady=15, sticky="w")
        ctk.CTkButton(sidebar_frame, text="Settings", font=nav_font, fg_color="transparent", text_color="white", anchor="w", hover_color="#1A1A1A").grid(row=3, column=0, pady=15, sticky="w")

    def _build_chat_area(self):
        chat_container = ctk.CTkFrame(self, fg_color=INNER_CONTAINER_BG, border_color=PURPLE_ACCENT, border_width=2, corner_radius=24)
        chat_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        chat_container.grid_rowconfigure(0, weight=1)
        chat_container.grid_rowconfigure(1, weight=12)
        chat_container.grid_rowconfigure(2, weight=2)
        chat_container.grid_columnconfigure(0, weight=1)
        
        models = list(self.MODEL_MAP.keys())
        
        self.model_dropdown = ctk.CTkOptionMenu(
            chat_container, 
            values=models, 
            fg_color=INNER_CONTAINER_BG,      
            button_color=INNER_CONTAINER_BG,  
            button_hover_color="#2A2A2A", 
            text_color="white", 
            font=("Helvetica", 16, "bold"), 
            dropdown_fg_color="#1A1A1A", 
            dropdown_text_color="white"
        )
        self.model_dropdown.grid(row=0, column=0, sticky="nw", padx=30, pady=30)
        
        self.chat_display = ctk.CTkScrollableFrame(chat_container, fg_color="transparent")
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        
        input_frame = ctk.CTkFrame(chat_container, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 30))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.prompt_entry = ctk.CTkEntry(input_frame, placeholder_text="Enter your prompt", height=60, corner_radius=30, fg_color="#222222", border_color=YELLOW_ACCENT, border_width=1, text_color="white", font=("Helvetica", 16))
        self.prompt_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        send_btn = ctk.CTkButton(input_frame, text="➔", font=("Helvetica", 20, "bold"), width=50, height=50, corner_radius=25, fg_color=YELLOW_ACCENT, hover_color="#E5D57F", text_color="black", command=self.handle_send_message)
        send_btn.grid(row=0, column=1, padx=(5, 0))

    def handle_send_message(self):
        user_text = self.prompt_entry.get().strip()
        if not user_text:
            return
            
        self.prompt_entry.delete(0, 'end')
        self._display_message("You", user_text, YELLOW_ACCENT)
        
        # Run the API call in a background thread to prevent UI freezing
        threading.Thread(target=self._fetch_ai_response, args=(user_text,), daemon=True).start()

    def _fetch_ai_response(self, user_text):
        selected_option = self.model_dropdown.get()
        
        if selected_option not in self.MODEL_MAP:
            self._display_message("System", "Please select a valid AI model.", PINK_ACCENT)
            return
            
        model_id, provider = self.MODEL_MAP[selected_option]
        
        # Format the message history for the API
        messages = [{"role": "user", "content": user_text}]
        
        # Fetch the response
        response = get_ai_response(messages, model_id, provider)
        
        # Display the AI response
        self._display_message("ALANX", response, PURPLE_ACCENT)

    def _display_message(self, role, text, color):
        # Use master.after to safely update the UI from the background thread
        self.after(0, self._render_bubble, role, text, color)

    def _render_bubble(self, role, text, color):
        # wraplength ensures long responses don't run off the edge of the screen
        lbl = ctk.CTkLabel(
            self.chat_display, 
            text=f"{role}:\n{text}", 
            text_color=color, 
            font=("Helvetica", 15), 
            justify="left", 
            anchor="w",
            wraplength=650
        )
        lbl.pack(fill="x", padx=10, pady=10)