import threading
import customtkinter as ctk
from core.theme import (
    COLOR_BACKGROUND, COLOR_SIDEBAR_BG, COLOR_CONTAINER_BG, COLOR_SURFACE_ELEVATED, COLOR_BORDER_SUBTLE,
    COLOR_PRIMARY, COLOR_HIGHLIGHT, COLOR_ACCENT, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED,
    FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_CODE, RADIUS_PREMIUM, RADIUS_PILL, PADDING_MEDIUM
)
from services.api_client import get_ai_response
from ui.shared.markdown_parser import CTkMarkdownParser 

class WorkspaceFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=COLOR_BACKGROUND)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)  
        self.grid_columnconfigure(1, weight=5)  
        
        # Track active streaming animation and loader states
        self.is_thinking = False
        self.current_thinking_frame = None
        
        self.MODEL_MAP = {
            "OpenRouter: Auto Free Router": ("openrouter/free", "openrouter"),
            "OpenRouter: Llama 3.3 70B (Free)": ("meta-llama/llama-3.3-70b-instruct:free", "openrouter"),
            "OpenRouter: Gemma 4 31B (Free)": ("google/gemma-4-31b-it:free", "openrouter"),
            "OpenRouter: Qwen 3 Coder (Free)": ("qwen/qwen3-coder:free", "openrouter"),
            "OpenRouter: GPT-OSS 20B (Free)": ("openai/gpt-oss-20b:free", "openrouter"),
            "OpenRouter: Nemotron 3 Ultra (Free)": ("nvidia/nemotron-3-ultra-550b-a55b:free", "openrouter"),
            "OpenRouter: DeepSeek R1 (Free)": ("deepseek/deepseek-r1:free", "openrouter"),
            "OpenRouter: Poolside Laguna M.1 (Free)": ("poolside/laguna-m.1:free", "openrouter")
        }
        
        self._build_sidebar()
        self._build_chat_area()

    def _build_sidebar(self):
        sidebar_frame = ctk.CTkFrame(self, fg_color=COLOR_SIDEBAR_BG, corner_radius=0, border_width=0)
        sidebar_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        sidebar_frame.grid_rowconfigure((0, 4), weight=1)
        
        logo_placeholder = ctk.CTkLabel(sidebar_frame, text="ALANX", font=FONT_TITLE, text_color=COLOR_HIGHLIGHT)
        logo_placeholder.grid(row=0, column=0, pady=(30, 0), padx=PADDING_MEDIUM, sticky="n")
        
        self.history_btn = ctk.CTkButton(
            sidebar_frame, text="History", font=FONT_HEADING, fg_color="transparent", 
            text_color=COLOR_TEXT_MAIN, anchor="w", hover_color=COLOR_SURFACE_ELEVATED,
            height=45, corner_radius=8
        )
        self.history_btn.grid(row=1, column=0, pady=10, padx=PADDING_MEDIUM, sticky="ew")
        
        self.profile_btn = ctk.CTkButton(
            sidebar_frame, text="Profile", font=FONT_HEADING, fg_color="transparent", 
            text_color=COLOR_TEXT_MAIN, anchor="w", hover_color=COLOR_SURFACE_ELEVATED,
            height=45, corner_radius=8
        )
        self.profile_btn.grid(row=2, column=0, pady=10, padx=PADDING_MEDIUM, sticky="ew")
        
        self.settings_btn = ctk.CTkButton(
            sidebar_frame, text="Settings", font=FONT_HEADING, fg_color="transparent", 
            text_color=COLOR_TEXT_MAIN, anchor="w", hover_color=COLOR_SURFACE_ELEVATED,
            height=45, corner_radius=8
        )
        self.settings_btn.grid(row=3, column=0, pady=10, padx=PADDING_MEDIUM, sticky="ew")

    def _build_chat_area(self):
        chat_container = ctk.CTkFrame(
            self, fg_color=COLOR_CONTAINER_BG, border_color=COLOR_PRIMARY, 
            border_width=1, corner_radius=RADIUS_PREMIUM
        )
        chat_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        chat_container.grid_rowconfigure(0, weight=1)   
        chat_container.grid_rowconfigure(1, weight=12)  
        chat_container.grid_rowconfigure(2, weight=2)   
        chat_container.grid_columnconfigure(0, weight=1)
        
        models = list(self.MODEL_MAP.keys())
        
        self.model_dropdown = ctk.CTkOptionMenu(
            chat_container, values=models, fg_color=COLOR_SURFACE_ELEVATED,      
            button_color=COLOR_SURFACE_ELEVATED, button_hover_color=COLOR_BORDER_SUBTLE, 
            text_color=COLOR_TEXT_MAIN, font=FONT_HEADING, 
            dropdown_fg_color=COLOR_SURFACE_ELEVATED, dropdown_text_color=COLOR_TEXT_MAIN,
            corner_radius=8
        )
        self.model_dropdown.grid(row=0, column=0, sticky="nw", padx=30, pady=25)
        
        self.chat_display = ctk.CTkScrollableFrame(chat_container, fg_color="transparent")
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 15))
        
        input_container = ctk.CTkFrame(chat_container, fg_color=COLOR_SURFACE_ELEVATED, corner_radius=RADIUS_PILL, height=64)
        input_container.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 30))
        input_container.grid_columnconfigure(0, weight=1)
        input_container.grid_propagate(False) 
        
        self.prompt_entry = ctk.CTkEntry(
            input_container, placeholder_text="Ask ALANX anything...", 
            fg_color="transparent", border_width=0, text_color=COLOR_TEXT_MAIN, 
            font=FONT_BODY, placeholder_text_color=COLOR_TEXT_MUTED
        )
        self.prompt_entry.grid(row=0, column=0, sticky="ew", padx=(25, 10), pady=12)
        
        # UI Reference Bound instance element for active state toggles
        self.send_btn = ctk.CTkButton(
            input_container, text="➔", font=FONT_HEADING, width=40, height=40, 
            corner_radius=20, fg_color=COLOR_HIGHLIGHT, hover_color="#E5D57F", 
            text_color="#000000", command=self.handle_send_message
        )
        self.send_btn.grid(row=0, column=1, padx=(0, 12), pady=12)

    def handle_send_message(self):
        user_text = self.prompt_entry.get().strip()
        if not user_text or self.is_thinking:
            return
            
        self.prompt_entry.delete(0, 'end')
        self._display_message("You", user_text, COLOR_HIGHLIGHT)
        
        self._show_thinking_indicator()
        
        threading.Thread(target=self._fetch_ai_response, args=(user_text,), daemon=True).start()

    def _fetch_ai_response(self, user_text):
        selected_option = self.model_dropdown.get()
        if selected_option not in self.MODEL_MAP:
            self.after(0, self._hide_thinking_indicator)
            self._display_message("System", "Please select a valid AI model.", COLOR_ACCENT)
            return
            
        model_id, provider = self.MODEL_MAP[selected_option]
        messages = [{"role": "user", "content": user_text}]
        
        response_dict = get_ai_response(messages, model_id, provider)
        content = response_dict.get("content", "")
        reasoning = response_dict.get("reasoning_details")

        # Safely tear down loader frames before animating incoming stream response
        self.after(0, self._hide_thinking_indicator)

        if isinstance(reasoning, list):
            reasoning_text = "\n".join([r.get("text", "") for r in reasoning if isinstance(r, dict)])
        else:
            reasoning_text = str(reasoning) if reasoning else None
            
        if reasoning_text and reasoning_text.strip() != "None":
            self._display_message("ALANX (Thinking Process)", reasoning_text, COLOR_TEXT_MUTED)
            
        self._display_message("ALANX", content, COLOR_PRIMARY)

    def _show_thinking_indicator(self):
        """Creates an isolated temporary indicator and locks the send toggle."""
        self.is_thinking = True
        self.send_btn.configure(state="disabled", fg_color=COLOR_BORDER_SUBTLE)
        
        self.current_thinking_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        self.current_thinking_frame.pack(fill="x", padx=10, pady=10)
        
        self.thinking_label = ctk.CTkLabel(
            self.current_thinking_frame, text="ALANX is thinking", 
            text_color=COLOR_TEXT_MUTED, font=("Helvetica", 14, "italic"), anchor="w"
        )
        self.thinking_label.pack(fill="x")
        self.chat_display._parent_canvas.yview_moveto(1.0)
        
        self._animate_thinking_dots(0)

    def _animate_thinking_dots(self, dot_count):
        """Calculates dot loops at steady micro-intervals."""
        if not self.is_thinking or not hasattr(self, 'thinking_label') or not self.thinking_label.winfo_exists():
            return
        dots = "." * (dot_count % 4)
        self.thinking_label.configure(text=f"ALANX is thinking{dots}")
        self.after(400, self._animate_thinking_dots, dot_count + 1)

    def _hide_thinking_indicator(self):
        """Destroys temporary loading frames safely on completion."""
        if self.current_thinking_frame and self.current_thinking_frame.winfo_exists():
            self.current_thinking_frame.destroy()
        self.current_thinking_frame = None

    def _display_message(self, role, text, color):
        self.after(0, self._render_bubble, role, text, color)

    def _animate_typing(self, label, full_text, current_index=0):
        if current_index < len(full_text):
            chunk_size = 3
            next_index = min(current_index + chunk_size, len(full_text))
            
            label.configure(text=full_text[:next_index])
            self.chat_display._parent_canvas.yview_moveto(1.0)
            self.after(10, self._animate_typing, label, full_text, next_index)
        else:
            # Re-enable input systems precisely after typing animation wraps up
            self.is_thinking = False
            self.send_btn.configure(state="normal", fg_color=COLOR_HIGHLIGHT)
            
            # --- THE STREAM-TO-SNAP SWAP ---
            parent_frame = label.master
            label.destroy()  # Remove the raw text label
            
            # Snap in the beautifully parsed Markdown UI
            parsed_view = CTkMarkdownParser(parent_frame, text=full_text)
            parsed_view.pack(fill="x", pady=2)
            
            self.chat_display._parent_canvas.yview_moveto(1.0)

    def _render_bubble(self, role, text, color):
        msg_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        msg_frame.pack(fill="x", padx=10, pady=10)
        
        role_lbl = ctk.CTkLabel(msg_frame, text=f"{role}:", text_color=color, font=("Helvetica", 15, "bold"), anchor="w")
        role_lbl.pack(fill="x", pady=(0, 5))
        
        if isinstance(text, dict):
            text = text.get("content", str(text))
        text = str(text)
        
        # We still split by code blocks (```) so Pygments can handle syntax highlighting later
        parts = text.split("```")
        for i, part in enumerate(parts):
            if not part.strip():
                continue
                
            if i % 2 == 0:
                # Standard text block mapping
                lbl = ctk.CTkLabel(
                    msg_frame, text="", text_color=COLOR_TEXT_MAIN, 
                    font=FONT_BODY, justify="left", anchor="w", wraplength=650
                )
                lbl.pack(fill="x", pady=2)
                lbl._associated_role = role
                
                if role in ["ALANX", "ALANX (Thinking Process)", "System"]:
                    # Stream AI text (it will snap to Markdown when finished)
                    self._animate_typing(lbl, part.strip())
                else:
                    # User messages skip streaming and snap to Markdown instantly
                    lbl.destroy()
                    parsed_view = CTkMarkdownParser(msg_frame, text=part.strip())
                    parsed_view.pack(fill="x", pady=2)
                    
                    self.chat_display._parent_canvas.yview_moveto(1.0)
                    self.send_btn.configure(state="normal", fg_color=COLOR_HIGHLIGHT)
            else:
                # ... (Keep your exact existing code block generation here untouched) ...
                lines = part.split('\n', 1)
                lang = lines[0].strip() if len(lines) > 1 else ""
                code_content = lines[1].strip() if len(lines) > 1 else part.strip()
                
                code_container = ctk.CTkFrame(msg_frame, fg_color="#1E1E1E", corner_radius=8, border_width=1, border_color=COLOR_BORDER_SUBTLE)
                code_container.pack(fill="x", padx=10, pady=5)
                
                if lang:
                    lang_lbl = ctk.CTkLabel(code_container, text=lang, text_color=COLOR_TEXT_MUTED, font=("Helvetica", 12, "italic"), anchor="w")
                    lang_lbl.pack(fill="x", padx=10, pady=(5, 0))
                
                line_count = len(code_content.split('\n'))
                box_height = min(400, max(60, line_count * 20))
                
                code_box = ctk.CTkTextbox(code_container, font=FONT_CODE, fg_color="transparent", text_color="#E6E6E6", height=box_height)
                code_box.insert("0.0", code_content)
                code_box.configure(state="disabled")
                code_box.pack(fill="x", padx=10, pady=10)