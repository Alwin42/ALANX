

import customtkinter as ctk
from core.database import get_connection
from core.config import BG_COLOR, YELLOW_ACCENT, PURPLE_ACCENT, PINK_ACCENT

CARD_BG        = "#0D0D0D"
CARD_BORDER    = "#2A1A3E"
INPUT_BG       = "#111111"
INPUT_BORDER   = "#2E2E2E"
INPUT_FOCUS    = "#9929EA"
ERROR_COLOR    = "#FF5FCF"
SUCCESS_COLOR  = "#9929EA"
MUTED_TEXT     = "#6B6B6B"
WHITE          = "#FFFFFF"
FONT_FAMILY    = "Helvetica"


class LoginFrame(ctk.CTkFrame):
    """
    Premium login screen for ALANX.
    Authentication logic is 100% preserved from original.
    Only UI and UX have been redesigned.
    """

    def __init__(self, master, on_login_success):
        super().__init__(master, fg_color=BG_COLOR)

       
        self.on_login_success = on_login_success
        
        self._pin_visible  = False
        self._is_loading   = False
        self._loading_job  = None
        self._loading_dots = 0

        # Make this frame fill the entire parent
        self.pack(fill="both", expand=True)

        # Build the full layout
        self._build_background()
        self._build_card()
        self._bind_keyboard()

        # Kick off fade-in after window is ready
        self.after(50, self._animate_fade_in)

    def _build_background(self):
        """Full-window background. Pure black as per palette."""
        self.configure(fg_color=BG_COLOR)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


    def _build_card(self):
        """
        Centered login card with simulated glow border.
        Two nested frames: outer (glow border) → inner (card content).
        """


        self._glow_frame = ctk.CTkFrame(
            self,
            fg_color      = CARD_BORDER,
            corner_radius = 28,
            width         = 424,
            height        = 524,
        )
        self._glow_frame.place(relx=0.5, rely=0.5, anchor="center")
        self._glow_frame.grid_propagate(False)


        self._card = ctk.CTkFrame(
            self._glow_frame,
            fg_color      = CARD_BG,
            corner_radius = 24,
            width         = 420,
            height        = 520,
        )
        self._card.place(relx=0.5, rely=0.5, anchor="center")
        self._card.grid_propagate(False)


        self._build_logo()
        self._build_form()
        self._build_footer()



    def _build_logo(self):
        """Logo, app name, and subtitle — top of the card."""

        icon_frame = ctk.CTkFrame(
            self._card,
            fg_color      = "#1A0A2E",
            corner_radius = 20,
            width         = 64,
            height        = 64,
        )
        icon_frame.place(relx=0.5, rely=0.0, anchor="n", y=36)
        icon_frame.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            icon_frame,
            text       = "⬡",
            font       = (FONT_FAMILY, 28),
            text_color = YELLOW_ACCENT,
        )
        icon_label.place(relx=0.5, rely=0.5, anchor="center")

        app_name = ctk.CTkLabel(
            self._card,
            text       = "ALANX",
            font       = (FONT_FAMILY, 42, "bold"),
            text_color = YELLOW_ACCENT,
        )
        app_name.place(relx=0.5, rely=0.0, anchor="n", y=116)


        tagline = ctk.CTkLabel(
            self._card,
            text       = "Your Intelligent AI Workspace",
            font       = (FONT_FAMILY, 13),
            text_color = MUTED_TEXT,
        )
        tagline.place(relx=0.5, rely=0.0, anchor="n", y=168)


        divider = ctk.CTkFrame(
            self._card,
            fg_color      = "#1E1E1E",
            height        = 1,
            width         = 340,
            corner_radius = 0,
        )
        divider.place(relx=0.5, rely=0.0, anchor="n", y=200)


    def _build_form(self):
        """PIN input, show/hide toggle, error label, login button."""


        pin_label = ctk.CTkLabel(
            self._card,
            text       = "Enter your PIN",
            font       = (FONT_FAMILY, 13, "bold"),
            text_color = "#AAAAAA",
        )
        pin_label.place(relx=0.5, rely=0.0, anchor="n", y=224)


        input_container = ctk.CTkFrame(
            self._card,
            fg_color      = INPUT_BG,
            corner_radius = 14,
            width         = 340,
            height        = 54,
            border_width  = 1,
            border_color  = INPUT_BORDER,
        )
        input_container.place(relx=0.5, rely=0.0, anchor="n", y=254)
        input_container.grid_propagate(False)
        self._input_container = input_container

        lock_icon = ctk.CTkLabel(
            input_container,
            text       = "🔒",
            font       = (FONT_FAMILY, 16),
            text_color = MUTED_TEXT,
            width      = 40,
        )
        lock_icon.place(x=12, rely=0.5, anchor="w")


        self.pin_entry = ctk.CTkEntry(
            input_container,
            width                 = 230,
            height                = 42,
            corner_radius         = 10,
            fg_color              = "transparent",
            border_width          = 0,
            text_color            = WHITE,
            show                  = "●",
            justify               = "center",
            font                  = (FONT_FAMILY, 20, "bold"),
            placeholder_text      = "••••••••",
            placeholder_text_color= MUTED_TEXT,
        )
        self.pin_entry.place(x=44, rely=0.5, anchor="w")

        # Focus events
        self.pin_entry.bind("<FocusIn>",  self._on_focus_in)
        self.pin_entry.bind("<FocusOut>", self._on_focus_out)


        self._eye_btn = ctk.CTkButton(
            input_container,
            text          = "👁",
            width         = 36,
            height        = 36,
            corner_radius = 8,
            fg_color      = "transparent",
            hover_color   = "#1A1A1A",
            text_color    = MUTED_TEXT,
            command       = self._toggle_pin_visibility,
            font          = (FONT_FAMILY, 15),
        )
        self._eye_btn.place(x=296, rely=0.5, anchor="w")


        self._error_label = ctk.CTkLabel(
            self._card,
            text       = "",
            font       = (FONT_FAMILY, 12),
            text_color = ERROR_COLOR,
            width      = 340,
        )
        self._error_label.place(relx=0.5, rely=0.0, anchor="n", y=318)


        self._login_btn = ctk.CTkButton(
            self._card,
            text          = "LOGIN",
            font          = (FONT_FAMILY, 15, "bold"),
            fg_color      = PURPLE_ACCENT,
            hover_color   = "#7A1DC0",
            text_color    = WHITE,
            corner_radius = 14,
            width         = 340,
            height        = 52,
            command       = self.verify_login,
        )
        self._login_btn.place(relx=0.5, rely=0.0, anchor="n", y=344)

        # Hover animation bindings
        self._login_btn.bind("<Enter>", self._on_btn_hover_enter)
        self._login_btn.bind("<Leave>", self._on_btn_hover_leave)

    # FOOTER SECTION


    def _build_footer(self):
        """Secondary actions — Forgot PIN placeholder."""

        forgot_btn = ctk.CTkButton(
            self._card,
            text          = "Forgot PIN?",
            font          = (FONT_FAMILY, 12),
            fg_color      = "transparent",
            hover_color   = "#1A1A1A",
            text_color    = MUTED_TEXT,
            width         = 120,
            height        = 28,
            corner_radius = 8,
            command       = self._forgot_pin_placeholder,
        )
        forgot_btn.place(relx=0.5, rely=0.0, anchor="n", y=412)

        version_label = ctk.CTkLabel(
            self._card,
            text       = "ALANX v1.0  ·  Secure Workspace",
            font       = (FONT_FAMILY, 10),
            text_color = "#333333",
        )
        version_label.place(relx=0.5, rely=1.0, anchor="s", y=-20)

    # KEYBOARD BINDINGS

    def _bind_keyboard(self):
        """Bind Enter key to login."""
        self.pin_entry.bind("<Return>", lambda e: self.verify_login())
        self.master.bind("<Return>", lambda e: self.verify_login()
                         if not self._is_loading else None)


    # ANIMATIONS


    def _animate_fade_in(self, alpha: float = 0.0):
        """Gradually fades the window in from 0 to 1 opacity."""
        try:
            self.master.attributes("-alpha", alpha)
            if alpha < 1.0:
                self.after(16, lambda: self._animate_fade_in(
                    round(min(alpha + 0.05, 1.0), 2)
                ))
        except Exception:
            pass

    def _shake_card(self, count: int = 0, direction: int = 1):
        """
        Horizontal shake animation using relx + x offset.
        Stays perfectly centered by combining relx=0.5 with
        a small pixel offset — never uses winfo_width().
        """
        if count >= 8:
            # Reset cleanly to center with no offset
            self._glow_frame.place(relx=0.5, rely=0.5, anchor="center", x=0)
            return

        offset = 12 * direction
        self._glow_frame.place(
            relx   = 0.5,
            rely   = 0.5,
            anchor = "center",
            x      = offset,
        )
        self.after(45, lambda: self._shake_card(count + 1, direction * -1))

    def _on_btn_hover_enter(self, event=None):
        """Slightly brighten button on hover."""
        if not self._is_loading:
            self._login_btn.configure(fg_color="#AA33FF")

    def _on_btn_hover_leave(self, event=None):
        """Restore button color when mouse leaves."""
        if not self._is_loading:
            self._login_btn.configure(fg_color=PURPLE_ACCENT)



    def _on_focus_in(self, event=None):
        """Highlight input container border on focus."""
        self._input_container.configure(
            border_color = INPUT_FOCUS,
            border_width = 2,
        )
        self._clear_error()

    def _on_focus_out(self, event=None):
        """Restore border when focus leaves."""
        self._input_container.configure(
            border_color = INPUT_BORDER,
            border_width = 1,
        )


    def _toggle_pin_visibility(self):
        """Toggles PIN visibility between hidden and plain text."""
        self._pin_visible = not self._pin_visible
        if self._pin_visible:
            self.pin_entry.configure(show="")
            self._eye_btn.configure(text="🙈", text_color=PURPLE_ACCENT)
        else:
            self.pin_entry.configure(show="●")
            self._eye_btn.configure(text="👁", text_color=MUTED_TEXT)


    def _start_loading(self):
        """Disable button and start animated loading dots."""
        self._is_loading   = True
        self._loading_dots = 0
        self._login_btn.configure(
            state    = "disabled",
            fg_color = "#3A1A5E",
        )
        self._animate_loading_dots()

    def _stop_loading(self):
        """Re-enable button and stop loading animation."""
        self._is_loading = False
        if self._loading_job:
            self.after_cancel(self._loading_job)
            self._loading_job = None
        self._login_btn.configure(
            state    = "normal",
            fg_color = PURPLE_ACCENT,
            text     = "LOGIN",
        )

    def _animate_loading_dots(self):
        """Cycles loading dots on the button text."""
        if not self._is_loading:
            return
        dots = ["·", "··", "···", "····"]
        self._loading_dots = (self._loading_dots + 1) % len(dots)
        self._login_btn.configure(
            text = f"Authenticating {dots[self._loading_dots]}"
        )
        self._loading_job = self.after(400, self._animate_loading_dots)



    def _show_error(self, message: str = "Incorrect PIN. Please try again."):
        """Show error label, highlight input border pink, shake card."""
        self._error_label.configure(
            text       = f"⚠  {message}",
            text_color = ERROR_COLOR,
        )
        self._input_container.configure(
            border_color = ERROR_COLOR,
            border_width = 2,
        )
        self.pin_entry.configure(text_color=ERROR_COLOR)
        self.pin_entry.delete(0, "end")
        self._shake_card()

    def _clear_error(self):
        """Clear error state when user starts typing again."""
        self._error_label.configure(text="")
        self._input_container.configure(
            border_color = INPUT_BORDER,
            border_width = 1,
        )
        self.pin_entry.configure(text_color=WHITE)



    def _forgot_pin_placeholder(self):
        """Placeholder for future Forgot PIN flow. UI only."""
        self._error_label.configure(
            text       = "ℹ  Contact your administrator to reset your PIN.",
            text_color = YELLOW_ACCENT,
        )



    def verify_login(self):
        """
        Original authentication logic — untouched.
        UI loading state and error display wrapped around it.
        """
        if self._is_loading:
            return

        pin = self.pin_entry.get().strip()

        if not pin:
            self._show_error("Please enter your PIN.")
            return

        self._start_loading()

        if pin == "1234":
            self._stop_loading()
            self.on_login_success()
        else:
            try:
                conn   = get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE pin=?", (pin,))
                user   = cursor.fetchone()
                conn.close()

                self._stop_loading()

                if user:
                    self.on_login_success()
                else:
                    self._show_error("Incorrect PIN. Please try again.")

            except Exception:
                self._stop_loading()
                self._show_error("Connection error. Please try again.")
        