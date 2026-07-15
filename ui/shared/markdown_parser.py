import customtkinter as ctk
from markdown_it import MarkdownIt
from core.theme import (
    COLOR_TEXT_MAIN, COLOR_TEXT_MUTED, COLOR_BORDER_SUBTLE, COLOR_SURFACE_ELEVATED,
    FONT_BODY, FONT_HEADING, FONT_CODE, FONT_TITLE
)

class CTkMarkdownParser(ctk.CTkFrame):
    def __init__(self, master, text, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        # Enable the table plugin extension during initialization
        self.md = MarkdownIt("commonmark").enable("table")
        self.raw_text = text
        
        self._render_ast()

    def _render_ast(self):
        # Generate the Abstract Syntax Tree tokens
        self.tokens = self.md.parse(self.raw_text)
        
        # State trackers for table generation
        table_frame = None
        current_row = 0
        current_col = 0
        
        for i, token in enumerate(self.tokens):
            if token.type == "inline":
                # Determine context based on the previous token
                parent_type = self.tokens[i-1].type if i > 0 else ""
                
                # --- 1. HANDLE TABLE CELLS (FIXED) ---
                if table_frame is not None and parent_type in ["th_open", "td_open"]:
                    is_header = (parent_type == "th_open")
                    bg_color = COLOR_BORDER_SUBTLE if is_header else COLOR_SURFACE_ELEVATED
                    # Use header font or bold body font if the text contained markdown bold asterisks
                    has_bold_markers = "**" in token.content
                    font = FONT_HEADING if (is_header or has_bold_markers) else FONT_BODY
                    
                    # Strip out the raw markdown bold/italic tags for display styling
                    clean_cell_text = token.content.replace("**", "").replace("*", "")
                    
                    cell = ctk.CTkFrame(table_frame, fg_color=bg_color, corner_radius=0, border_width=1, border_color=COLOR_BORDER_SUBTLE)
                    cell.grid(row=current_row, column=current_col, sticky="nsew", padx=1, pady=1)
                    
                    lbl = ctk.CTkLabel(cell, text=clean_cell_text, font=font, text_color=COLOR_TEXT_MAIN, wraplength=250)
                    lbl.pack(padx=10, pady=8)
                    current_col += 1
                    
                # --- 2. HANDLE HEADINGS ---
                elif parent_type == "heading_open":
                    lbl = ctk.CTkLabel(self, text=token.content, font=FONT_TITLE, text_color=COLOR_TEXT_MAIN, anchor="w", justify="left")
                    lbl.pack(fill="x", pady=(15, 5))
                    
                # --- 3. HANDLE STANDARD PARAGRAPHS & LISTS ---
                else:
                    clean_text = token.content.replace("**", "").replace("*", "")
                    if clean_text.strip():
                        prefix = "•  " if parent_type == "list_item_open" else ""
                        lbl = ctk.CTkLabel(self, text=f"{prefix}{clean_text}", font=FONT_BODY, text_color=COLOR_TEXT_MAIN, anchor="w", justify="left", wraplength=650)
                        lbl.pack(fill="x", pady=2, padx=(20 if prefix else 0, 0))
            
            # --- 4. TABLE GRID MANAGEMENT ---
            elif token.type == "table_open":
                table_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=8, border_width=1, border_color=COLOR_BORDER_SUBTLE)
                table_frame.pack(fill="x", padx=10, pady=15)
                current_row = 0
            elif token.type == "tr_open":
                current_col = 0
            elif token.type == "tr_close":
                current_row += 1
            elif token.type == "table_close":
                table_frame = None
                
            # --- 5. CODE BLOCK MANAGEMENT ---
            elif token.type == "fence" or token.type == "code_block":
                lang = token.info.strip() if token.info else "code"
                code_content = token.content.strip()
                
                code_container = ctk.CTkFrame(self, fg_color="#1E1E1E", corner_radius=8, border_width=1, border_color=COLOR_BORDER_SUBTLE)
                code_container.pack(fill="x", padx=10, pady=10)
                
                if lang:
                    lang_lbl = ctk.CTkLabel(code_container, text=lang, text_color=COLOR_TEXT_MUTED, font=("Helvetica", 12, "italic"), anchor="w")
                    lang_lbl.pack(fill="x", padx=10, pady=(5, 0))
                
                line_count = len(code_content.split('\n'))
                box_height = min(400, max(60, line_count * 20))
                
                code_box = ctk.CTkTextbox(code_container, font=FONT_CODE, fg_color="transparent", text_color="#E6E6E6", height=box_height)
                code_box.insert("0.0", code_content)
                code_box.configure(state="disabled")
                code_box.pack(fill="x", padx=10, pady=10)