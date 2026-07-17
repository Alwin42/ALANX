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
        
        # Track active streaming animation, loader states, and responsiveness
        self.is_thinking = False
        self.current_thinking_frame = None
        self.is_first_message = True
        self.message_labels = [] 
        
        self.MODEL_MAP = {
            # --- CATEGORY 2: STABLE & HIGHLY RESPONSIVE (FREE) ---
            "Meta: Llama 3.2 3B Instruct (Stable)": ("meta-llama/llama-3.2-3b-instruct:free", "openrouter"),
            "Google: Gemma 4 31B (Stable)": ("google/gemma-4-31b-it:free", "openrouter"),
            "Google: Gemma 4 26B A4B (Stable)": ("google/gemma-4-26b-a4b-it:free", "openrouter"),
            "NVIDIA: Nemotron 3 Nano 30B (Stable)": ("nvidia/nemotron-3-nano-30b-a3b:free", "openrouter"),
            "NVIDIA: Nemotron Nano 12B VL (Stable)": ("nvidia/nemotron-nano-12b-2-vl:free", "openrouter"),
            "NVIDIA: Nemotron Nano 9B V2 (Stable)": ("nvidia/nemotron-nano-9b-v2:free", "openrouter"),
            
            # --- CATEGORY 3: FLAGSHIPS [HEAVILY RATE-LIMITED] ---
            "OpenAI: GPT-OSS 20B [RATE-LIMITED]": ("openai/gpt-oss-20b:free", "openrouter"),
            "Meta: Llama 3.3 70B [RATE-LIMITED]": ("meta-llama/llama-3.3-70b-instruct:free", "openrouter"),
            "NVIDIA: Nemotron 3 Super [RATE-LIMITED]": ("nvidia/nemotron-3-super:free", "openrouter"),
            "Qwen: Qwen3 Next 80B [RATE-LIMITED]": ("qwen/qwen3-next-80b-a3b-instruct:free", "openrouter"),
            "Qwen: Qwen3 Coder 480B [RATE-LIMITED]": ("qwen/qwen3-coder-480b-a35b:free", "openrouter"),
            
            # --- OPENROUTER AUTO-ROUTER (FALLBACK) ---
            "OpenRouter: Auto Free Router": ("openrouter/free", "openrouter"),
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
            self, fg_color=COLOR_CONTAINER_BG, border_color=COLOR_BORDER_SUBTLE, 
            border_width=1, corner_radius=RADIUS_PREMIUM
        )
        chat_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Refined row weights for better expansion
        chat_container.grid_rowconfigure(0, weight=0)   
        chat_container.grid_rowconfigure(1, weight=1)  
        chat_container.grid_rowconfigure(2, weight=0)   
        chat_container.grid_columnconfigure(0, weight=1)
        
        # --- 1. Minimalist Header ---
        header_frame = ctk.CTkFrame(chat_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        models = list(self.MODEL_MAP.keys())
        
        self.model_dropdown = ctk.CTkOptionMenu(
            header_frame, values=models, fg_color=COLOR_SURFACE_ELEVATED,      
            button_color=COLOR_SURFACE_ELEVATED, button_hover_color=COLOR_BORDER_SUBTLE, 
            text_color=COLOR_TEXT_MAIN, font=FONT_HEADING, 
            dropdown_fg_color=COLOR_SURFACE_ELEVATED, dropdown_text_color=COLOR_TEXT_MAIN,
            corner_radius=8, width=320, dynamic_resizing=False
        )
        self.model_dropdown.grid(row=0, column=0, sticky="w")

        # System Status Indicator
        self.status_indicator = ctk.CTkLabel(
            header_frame, text="● System Ready", text_color=COLOR_HIGHLIGHT, font=FONT_BODY
        )
        self.status_indicator.grid(row=0, column=1, sticky="e", padx=10)
        
        # --- 2. Responsive Chat Display ---
        self.chat_display = ctk.CTkScrollableFrame(chat_container, fg_color="transparent")
        self.chat_display.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        self.chat_display.bind("<Configure>", self._on_chat_resize)
        
        # --- 3. Polished Input Area ---
        input_container = ctk.CTkFrame(
            chat_container, fg_color=COLOR_SURFACE_ELEVATED, 
            corner_radius=RADIUS_PILL, border_width=1, border_color=COLOR_BORDER_SUBTLE
        )
        # Removed fixed height; relies on internal padding for dynamic scaling
        input_container.grid(row=2, column=0, sticky="ew", padx=30, pady=(0, 30))
        input_container.grid_columnconfigure(0, weight=1)
        
        self.prompt_entry = ctk.CTkEntry(
            input_container, placeholder_text="Ask ALANX anything...", 
            fg_color="transparent", border_width=0, text_color=COLOR_TEXT_MAIN, 
            font=FONT_BODY, placeholder_text_color=COLOR_TEXT_MUTED, height=45
        )
        self.prompt_entry.grid(row=0, column=0, sticky="ew", padx=(25, 10), pady=10)
        
        # Input focus highlighting
        self.prompt_entry.bind("<FocusIn>", lambda e: input_container.configure(border_color=COLOR_PRIMARY))
        self.prompt_entry.bind("<FocusOut>", lambda e: input_container.configure(border_color=COLOR_BORDER_SUBTLE))
        self.prompt_entry.bind("<Return>", lambda e: self.handle_send_message())
        
        self.send_btn = ctk.CTkButton(
            input_container, text="➔", font=FONT_HEADING, width=40, height=40, 
            corner_radius=20, fg_color=COLOR_HIGHLIGHT, hover_color="#E5D57F", 
            text_color="#000000", command=self.handle_send_message
        )
        self.send_btn.grid(row=0, column=1, padx=(0, 12), pady=10)

        # Initialize the landing view
        self._show_empty_state()

    def _show_empty_state(self):
        """Renders a premium, minimalist greeting before the first message."""
        self.empty_state_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        self.empty_state_frame.pack(expand=True, fill="both", pady=80)
        
        welcome_lbl = ctk.CTkLabel(
            self.empty_state_frame, text="How can I help you today?", 
            font=FONT_TITLE, text_color=COLOR_TEXT_MAIN
        )
        welcome_lbl.pack(pady=(0, 10))
        
        sub_lbl = ctk.CTkLabel(
            self.empty_state_frame, text="Your local workspace is ready and connected.", 
            font=FONT_BODY, text_color=COLOR_TEXT_MUTED
        )
        sub_lbl.pack()

    def _on_chat_resize(self, event):
        """Dynamically calculates and applies wraplength based on window size."""
        # Calculate optimal wrap length (leave room for scrollbar and padding)
        new_wraplength = max(350, event.width - 120)
        for lbl in self.message_labels:
            if lbl.winfo_exists():
                lbl.configure(wraplength=new_wraplength)

    def handle_send_message(self):
        user_text = self.prompt_entry.get().strip()
        if not user_text or self.is_thinking:
            return
            
        # Tear down empty state on first interaction
        if self.is_first_message:
            if hasattr(self, 'empty_state_frame') and self.empty_state_frame.winfo_exists():
                self.empty_state_frame.destroy()
            self.is_first_message = False
            
        self.prompt_entry.delete(0, 'end')
        self._display_message("You", user_text, COLOR_TEXT_MAIN)
        
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

        self.after(0, self._hide_thinking_indicator)

        if isinstance(reasoning, list):
            reasoning_text = "\n".join([r.get("text", "") for r in reasoning if isinstance(r, dict)])
        else:
            reasoning_text = str(reasoning) if reasoning else None
            
        if reasoning_text and reasoning_text.strip() != "None":
            self._display_message("ALANX (Thinking Process)", reasoning_text, COLOR_TEXT_MUTED)
            
        self._display_message("ALANX", content, COLOR_PRIMARY)

    def _show_thinking_indicator(self):
        self.is_thinking = True
        self.send_btn.configure(state="disabled", fg_color=COLOR_BORDER_SUBTLE)
        self.status_indicator.configure(text="● Processing...", text_color=COLOR_ACCENT)
        
        self.current_thinking_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        self.current_thinking_frame.pack(fill="x", padx=10, pady=10)
        
        self.thinking_label = ctk.CTkLabel(
            self.current_thinking_frame, text="ALANX is thinking", 
            text_color=COLOR_TEXT_MUTED, font=FONT_BODY, anchor="w"
        )
        self.thinking_label.pack(fill="x")
        self.chat_display._parent_canvas.yview_moveto(1.0)
        
        self._animate_thinking_dots(0)

    def _animate_thinking_dots(self, dot_count):
        if not self.is_thinking or not hasattr(self, 'thinking_label') or not self.thinking_label.winfo_exists():
            return
        dots = "." * (dot_count % 4)
        self.thinking_label.configure(text=f"ALANX is thinking{dots}")
        self.after(400, self._animate_thinking_dots, dot_count + 1)

    def _hide_thinking_indicator(self):
        if self.current_thinking_frame and self.current_thinking_frame.winfo_exists():
            self.current_thinking_frame.destroy()
        self.current_thinking_frame = None
        self.status_indicator.configure(text="● System Ready", text_color=COLOR_HIGHLIGHT)

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
            self.is_thinking = False
            self.send_btn.configure(state="normal", fg_color=COLOR_HIGHLIGHT)
            
            parent_frame = label.master
            
            # Clean up tracking list before destroying
            if label in self.message_labels:
                self.message_labels.remove(label)
                
            label.destroy() 
            
            parsed_view = CTkMarkdownParser(parent_frame, text=full_text)
            parsed_view.pack(fill="x", pady=2)
            
            self.chat_display._parent_canvas.yview_moveto(1.0)

    def _render_bubble(self, role, text, color):
        # --- 1. OPTIONAL THINKING ACCORDION DROPDOWN ---
        if role == "ALANX (Thinking Process)":
            msg_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
            msg_frame.pack(fill="x", padx=10, pady=4)
            
            content_box = [None]
            
            def toggle_thinking():
                if toggle_btn.cget("text").startswith("▶"):
                    toggle_btn.configure(text="▼ Hide Thinking Process", text_color=COLOR_PRIMARY)
                    if not content_box[0]:
                        content_box[0] = CTkMarkdownParser(msg_frame, text=text)
                    content_box[0].pack(fill="x", padx=20, pady=5)
                    self.chat_display._parent_canvas.yview_moveto(1.0)
                else:
                    toggle_btn.configure(text="▶ Show Thinking Process", text_color=COLOR_TEXT_MUTED)
                    if content_box[0]:
                        content_box[0].pack_forget()
            
            toggle_btn = ctk.CTkButton(
                msg_frame, text="▶ Show Thinking Process", font=FONT_BODY,
                fg_color="transparent", text_color=COLOR_TEXT_MUTED,
                hover_color=COLOR_SURFACE_ELEVATED, anchor="w", height=30, width=180,
                corner_radius=6, command=toggle_thinking
            )
            toggle_btn.pack(anchor="w", pady=2)
            return

        # --- 2. STANDARD CHAT BUBBLE SYSTEM ---
        msg_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        msg_frame.pack(fill="x", padx=10, pady=12)
        
        # User vs AI Visual Hierarchy
        if role == "You":
            # Distinct user bubble presentation (slightly inset, distinct background card)
            content_wrapper = ctk.CTkFrame(
                msg_frame, fg_color=COLOR_SURFACE_ELEVATED, 
                corner_radius=12, border_width=1, border_color=COLOR_BORDER_SUBTLE
            )
            # Align right by padding the left side heavily if desired, or keep it standard left with distinct card background
            content_wrapper.pack(anchor="e", fill="x", padx=(40, 0), pady=2) 
            
            role_lbl = ctk.CTkLabel(content_wrapper, text="You", text_color=COLOR_TEXT_MUTED, font=FONT_HEADING, anchor="w")
            role_lbl.pack(fill="x", padx=15, pady=(10, 2))
            
            parent_for_content = content_wrapper
            align_kwargs = {"padx": 15, "pady": (0, 10)}
        else:
            # AI messages are flush and clean
            role_lbl = ctk.CTkLabel(msg_frame, text=role, text_color=color, font=FONT_HEADING, anchor="w")
            role_lbl.pack(fill="x", pady=(0, 5))
            
            parent_for_content = msg_frame
            align_kwargs = {"padx": 0, "pady": 2}
        
        if isinstance(text, dict):
            text = text.get("content", str(text))
        text = str(text)
        
        parts = text.split("```")
        
        # Get current canvas width for immediate wraplength calculation
        current_width = self.chat_display.winfo_width()
        active_wraplength = max(350, current_width - 120) if current_width > 120 else 650

        for i, part in enumerate(parts):
            if not part.strip():
                continue
                
            if i % 2 == 0:
                lbl = ctk.CTkLabel(
                    parent_for_content, text="", text_color=COLOR_TEXT_MAIN, 
                    font=FONT_BODY, justify="left", anchor="w", wraplength=active_wraplength
                )
                lbl.pack(fill="x", **align_kwargs)
                lbl._associated_role = role
                self.message_labels.append(lbl) # Track for resizing
                
                if role in ["ALANX", "System"]:
                    self._animate_typing(lbl, part.strip())
                else:
                    lbl.destroy()
                    parsed_view = CTkMarkdownParser(parent_for_content, text=part.strip())
                    parsed_view.pack(fill="x", **align_kwargs)
                    self.chat_display._parent_canvas.yview_moveto(1.0)
            else:
                lines = part.split('\n', 1)
                lang = lines[0].strip() if len(lines) > 1 else ""
                code_content = lines[1].strip() if len(lines) > 1 else part.strip()
                
                # Polished Code Block matching the new dark theme
                code_container = ctk.CTkFrame(
                    parent_for_content, fg_color="#0A0A0A", corner_radius=8, 
                    border_width=1, border_color=COLOR_BORDER_SUBTLE
                )
                code_container.pack(fill="x", padx=10, pady=5)
                
                if lang:
                    lang_lbl = ctk.CTkLabel(code_container, text=lang, text_color=COLOR_TEXT_MUTED, font=FONT_BODY, anchor="w")
                    lang_lbl.pack(fill="x", padx=10, pady=(5, 0))
                
                line_count = len(code_content.split('\n'))
                box_height = min(400, max(60, line_count * 20))
                
                code_box = ctk.CTkTextbox(code_container, font=FONT_CODE, fg_color="transparent", text_color="#E6E6E6", height=box_height)
                code_box.insert("0.0", code_content)
                code_box.configure(state="disabled")
                code_box.pack(fill="x", padx=10, pady=10)